下述是我的测试代码
test.py
import os
from typing import Optional, Dict
import sys
from pathlib import Path
from libs.algo_core.api.video_api import add_subtitle
from libs.algo_core.utils.subtitle_utils import SubtitleTemplateConfig 

# --- 关键：将项目根目录 'algorithm' 添加到 Python 路径中 ---
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from libs.algo_core.utils import utils
utils.set_project_root(str(project_root))

# 黑底
# input_video = "/home/zhanglingwen/Algorithm/business-algo/data/input.mp4"
# 白底
input_video = "/home/zhanglingwen/Algorithm/business-algo/data/16_9.mp4"
input_srt = "/home/zhanglingwen/Algorithm/business-algo/data/output/input.json"
output_video = "/home/zhanglingwen/Algorithm/business-algo/data/video/classic_black.mp4"

if not os.path.exists(input_video):
    print(f"错误: 输入视频文件不存在 -> {input_video}")
elif not os.path.exists(input_srt):
    print(f"错误: 输入字幕文件不存在 -> {input_srt}")
else:
    config_instance = SubtitleTemplateConfig(
        input_video_path=input_video,
        output_video_path=output_video,
		# 这里传入的时josn字幕文件
        input_srt_path=input_srt,

        font_size=32,
        original_language="en",
        template_name="classic_black",
        subtitle_position="bottom",
    )

    # 4. 定义一个简单的回调函数来查看进度 (可选)
    def progress_callback(progress: int):
        print(f"处理中... {progress}%")

    print("开始处理视频...")
    # 5. 调用函数，并传入【类的实例】
    res_code, res_message = add_subtitle(config_instance, callback=progress_callback)
    
    # 打印最终结果
    print("\n--------------------------")
    print("处理完成！")
    print(f"  返回码: {res_code}")
    print(f"  返回信息: {res_message}")
    print("--------------------------")

video_api.py
这里调过去的
def add_subtitle(
    config:SubtitleTemplateConfig, 
    callback: Optional[Callable[[int], None]] = None
)-> Tuple[int, str]:
    """
    对外提供给视频添加字幕的接口
    返回错误码
    """
    return VideoSubtitleApplier.apply_template(
        config=config, 
        callback=callback
    )


下述是我的字幕绘制核心代码
# 下述是我添加字幕的核心逻辑代码
# video_subtitle_applier.py

import os
import re
import numpy as np
from moviepy import VideoFileClip, CompositeVideoClip, ImageClip
import pysubs2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import List, Tuple, Optional, Callable, Dict, Any
from copy import deepcopy

# ----------------- 关键依赖 -----------------
from ..utils import utils, video_utils
from ..api.error_codes import ErrorCodes
from ..utils.subtitle_utils import SubtitleTemplateConfig, remove_punctuation_from_end
from ..utils.subtitle_style_config import SubtitleTemplate, STYLE_LIBRARY, DEFAULT_TEMPLATE, get_font_for_language
from ..utils.subtitle_position_config import VIDEO_SPEC_CONFIG
# -------------------------------------------

class VideoSubtitleApplier:
    _singleton = None

    def __init__(self, config: SubtitleTemplateConfig, callback: Optional[Callable[[int], None]] = None):
        self.config = config
        self.callback = callback
        self._validate_paths()
        self.loaded_fonts = {}

    @classmethod
    def _get_instance(cls, config: SubtitleTemplateConfig, callback: Optional[Callable[[int], None]] = None):
        if cls._singleton is None:
            cls._singleton = cls(config, callback)
        else:
            cls._singleton.config = config
            cls._singleton.callback = callback
            cls._singleton.loaded_fonts = {}
        return cls._singleton

    @staticmethod
    def apply_template(config: SubtitleTemplateConfig, callback: Optional[Callable[[int], None]] = None) -> Tuple[int, str]:
        try:
            inst = VideoSubtitleApplier._get_instance(config, callback)
            return inst._apply_template_to_video()
        except (ValueError, FileNotFoundError) as e:
            msg = f"初始化失败: {e}"
            utils.print2(msg)
            if "字幕路径缺失" in str(e):
                return ErrorCodes.VIDEO_ORIGINAL_SUBTITLE_MISSING[0], msg
            if "字体文件" in str(e):
                return ErrorCodes.VIDEO_FONT_NOT_FOUND[0], msg
            if "模板未找到" in str(e):
                 return ErrorCodes.INVALID_INPUT[0], msg
            return ErrorCodes.INVALID_INPUT[0], msg

    # ---------------- 新增：布局配置获取函数 ----------------
    def _get_layout_config(self, video: VideoFileClip) -> Dict[str, Any]:
        ratio = round(float(video.w) / float(video.h), 2)
        if abs(ratio - (9.0/16.0)) < 0.05:
            ratio_key = "9:16"
        else:
            ratio_key = "default_ratio"

        utils.print2(f"检测到视频比例约为 {ratio:.2f}，匹配配置 '{ratio_key}'")
        spec = VIDEO_SPEC_CONFIG.get(ratio_key, VIDEO_SPEC_CONFIG["default_ratio"])

        subtitle_pos = (self.config.subtitle_position or "bottom")
        layout_cfg = spec["layout_config"].get(subtitle_pos, spec["layout_config"].get("bottom"))

        lang = (self.config.original_language or "").lower()
        line_break_rules = spec.get("line_break_rules", {})
        rule = None
        if lang in line_break_rules:
            rule = line_break_rules[lang]
        elif '-' in lang:
            base = lang.split('-')[0]
            for k in line_break_rules.keys():
                if k.lower() == base:
                    rule = line_break_rules[k]
                    break

        if rule:
            max_chars_per_line = rule.get("max_chars_per_line", layout_cfg.get("default_max_chars_per_line", 25))
            max_lines = rule.get("max_lines", layout_cfg.get("default_max_lines", 2))
        else:
            max_chars_per_line = layout_cfg.get("default_max_chars_per_line", layout_cfg.get("max_chars_per_line", 25))
            max_lines = layout_cfg.get("default_max_lines", layout_cfg.get("max_lines", 2))

        layout_cfg["max_chars_per_line"] = max_chars_per_line
        layout_cfg["max_lines"] = max_lines
        layout_cfg["ratio_key"] = ratio_key

        utils.print2(f"布局选择: 位置={subtitle_pos}, 每行最多字符={max_chars_per_line}, 最多行={max_lines}")
        return layout_cfg

    def _validate_paths(self):
        if not self.config.input_video_path or not os.path.exists(self.config.input_video_path):
            raise FileNotFoundError(f"输入视频文件未找到: {self.config.input_video_path}")
        if not self.config.input_srt_path or not os.path.exists(self.config.input_srt_path):
            raise FileNotFoundError(f"输入字幕文件未找到: {self.config.input_srt_path}")
        if self.config.template_name not in STYLE_LIBRARY:
            raise ValueError(f"字幕模板未在样式库中找到: '{self.config.template_name}'")

    def _load_font(self, font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
        font_key = f"{font_name}_{font_size}"
        if font_key in self.loaded_fonts:
            return self.loaded_fonts[font_key]
        project_root = utils.get_project_root()
        if project_root is None:
            raise FileNotFoundError("无法找到项目根目录。")

        fonts_dir = os.path.join(project_root, 'res', 'fonts')
        font_path = os.path.join(fonts_dir, font_name)

        if not os.path.exists(font_path):
            font_path_static = os.path.join(fonts_dir, 'static', font_name)
            if os.path.exists(font_path_static):
                font_path = font_path_static
            else:
                common_suffixes = ['.ttf', '.otf', '.ttc']
                found = False
                for suffix in common_suffixes:
                    if os.path.exists(font_path + suffix):
                        font_path += suffix
                        found = True
                        break
                if not found:
                    raise FileNotFoundError(f"字体文件 '{font_name}' 在默认目录中未找到。")

        utils.print2(f"加载字体: {font_path}, 字号: {font_size}")
        font = ImageFont.truetype(font_path, font_size)
        self.loaded_fonts[font_key] = font
        return font

    def _apply_template_to_video(self) -> Tuple[int, str]:
        utils.print2("开始应用字幕模板处理视频...")
        video, final_video = None, None
        try:
            if self.callback: self.callback(5)
            video = VideoFileClip(self.config.input_video_path)
            subtitle_clips = self._create_subtitle_clips(video)
            if not subtitle_clips:
                utils.print2("警告: 未生成任何字幕剪辑。视频将不含字幕。")
            utils.print2("合成视频和字幕剪辑...")
            final_video = CompositeVideoClip([video] + subtitle_clips, size=video.size)
            if self.callback: self.callback(85)
            write_code = video_utils.write_video_with_post_processing(final_video, self.config.output_video_path)
            if write_code != ErrorCodes.SUCCESS:
                msg = f"视频处理完成，但写入文件失败! 文件:{self.config.output_video_path}, 错误码:{write_code}"
                utils.print2(msg)
                return ErrorCodes.VIDEO_SUBTITLE_PROCESSING_ERROR[0], msg
            utils.print2("视频处理成功完成。")
            return ErrorCodes.SUCCESS, "处理成功"
        except Exception as e:
            msg = f"处理视频时出错: {e}"
            utils.print2(msg)
            import traceback
            traceback.print_exc()
            if isinstance(e, FileNotFoundError):
                return ErrorCodes.VIDEO_FONT_NOT_FOUND[0], msg
            return ErrorCodes.VIDEO_SUBTITLE_PROCESSING_ERROR[0], msg
        finally:
            if video: video.close()
            if final_video: final_video.close()
            if self.callback: self.callback(100)

    def _resolve_template(self) -> SubtitleTemplate:
        """
        三级优先级（运行时 > 模板 > 默认）合并配置。
        并在此阶段做旧字段到投影字段的映射，保持兼容。
        """
        resolved_config = deepcopy(DEFAULT_TEMPLATE)

        custom_overrides = STYLE_LIBRARY.get(self.config.template_name)
        if custom_overrides:
            for key, value in custom_overrides.items():
                if hasattr(resolved_config, key):
                    setattr(resolved_config, key, value)

        # 动态选择字体（优先模板 font_map）
        if self.config.original_language:
            resolved_config.font_name = get_font_for_language(
                self.config.original_language,
                getattr(resolved_config, "font_map", None),
                fallback_font_name=resolved_config.font_name
            )

        # 覆盖字号
        if self.config.font_size is not None:
            resolved_config.font_size = self.config.font_size

        # 关键词列表覆盖
        if self.config.keywords_override is not None:
            resolved_config.keywords = self.config.keywords_override

        # ---------- 旧阴影字段 → 新投影字段 的兼容映射 ----------
        # 若用户或旧模板设置了 shadow_*（旧字段），而新投影未开启，则自动映射到投影配置
        if (not resolved_config.enable_drop_shadow) and (resolved_config.drop_shadow_color is None):
            if resolved_config.shadow_color is not None:
                resolved_config.enable_drop_shadow = True
                resolved_config.drop_shadow_color = resolved_config.shadow_color
                resolved_config.drop_shadow_offset = resolved_config.shadow_offset
                resolved_config.drop_shadow_blur = resolved_config.shadow_blur
        # -----------------------------------------------------

        return resolved_config

    def _create_subtitle_clips(self, video: VideoFileClip) -> List[ImageClip]:
        template = self._resolve_template()
        utils.print2(f"使用模板 '{self.config.template_name}' 生成字幕...")

        layout = self._get_layout_config(video)
        final_position = layout.get("position_y", self.config.subtitle_position or "bottom")
        offset_y = layout.get("offset_y", 0)

        subs = pysubs2.load(self.config.input_srt_path, encoding='utf-8')
        subtitles = [(e.start, e.end, e.plaintext) for e in subs]
        clips = []
        total_subs = len(subtitles)
        if total_subs == 0:
            utils.print2("未检测到字幕内容。")
            return clips

        for i, (start_ms, end_ms, text) in enumerate(subtitles):
            text = remove_punctuation_from_end(text)
            duration = (end_ms - start_ms) / 1000.0
            start_sec = start_ms / 1000.0
            if duration <= 0:
                continue

            img_array = self._draw_text_with_keywords(
                text=text,
                video_w=video.w,
                template=template,
                max_chars_per_line=layout["max_chars_per_line"],
                max_lines=layout["max_lines"]
            )

            if img_array is not None:
                img_h = img_array.shape[0]
                if final_position == 'bottom':
                    y_pos = video.h - img_h - offset_y
                elif final_position == 'top':
                    y_pos = offset_y
                else:
                    y_pos = (video.h - img_h) // 2

                clip = (
                    ImageClip(img_array)
                    .with_duration(duration)
                    .with_position(('center', y_pos))
                    .with_start(start_sec)
                )
                clips.append(clip)

            if self.callback:
                self.callback(int(5 + 80 * (i + 1) / total_subs))

        return clips

    def _draw_text_with_keywords(
            self,
            text: str,
            video_w: int,
            template: SubtitleTemplate,
            max_chars_per_line: int,
            max_lines: int
        ) -> Optional[np.ndarray]:

        if not text.strip():
            return None

        font = self._load_font(template.font_name, template.font_size)

        # 1) 计算可用最大像素宽度
        max_width = video_w - (template.bg_padding_x + template.stroke_width + 5) * 2
        if max_width <= 0:
            max_width = int(video_w * 0.9)

        lines: List[str] = []
        current_line = ""

        keyword_set = {kw.lower() for kw in (template.keywords or [])}

        # 区分 CJK 与 非 CJK
        is_cjk = bool(re.search(r"[\u4e00-\u9fff]", text))
        if is_cjk:
            # CJK：按字符换行（不受单词间距影响）
            for ch in text:
                if len(current_line) >= max_chars_per_line:
                    lines.append(current_line)
                    current_line = ch
                else:
                    if font.getlength(current_line + ch) > max_width and current_line:
                        lines.append(current_line)
                        current_line = ch
                    else:
                        current_line += ch
        else:
            # 英文等：按词换行，并把“单词间距”计入宽度计算
            words = text.split()
            for w in words:
                if not current_line:
                    if font.getlength(w) <= max_width:
                        current_line = w
                    else:
                        current_line = w
                else:
                    candidate_text = current_line + " " + w
                    candidate_width = font.getlength(candidate_text) + template.word_spacing_px
                    if candidate_width <= max_width and len(current_line) < max_chars_per_line:
                        current_line = candidate_text
                    else:
                        lines.append(current_line)
                        current_line = w

            if current_line:
                lines.append(current_line)

        # 限制行数
        if len(lines) > max_lines:
            lines = lines[:max_lines]
        if not lines:
            return None

        # 2) 计算文本尺寸
        ascent, descent = font.getmetrics()
        line_height = ascent + descent + template.line_spacing
        total_text_height = (len(lines) * line_height) - template.line_spacing

        def measure_line_width(line: str) -> float:
            if is_cjk or template.word_spacing_px <= 0:
                return font.getlength(line)
            tokens = re.findall(r'\s+|[^\s]+', line)
            extra_spaces = sum(1 for t in tokens if t.isspace())
            return font.getlength(line) + extra_spaces * template.word_spacing_px

        max_line_width = max(measure_line_width(line) for line in lines)

        # 3) 创建画布
        canvas_width = max_line_width + 2 * (template.bg_padding_x + template.stroke_width)
        canvas_height = total_text_height + 2 * (template.bg_padding_y + template.stroke_width)
        canvas_width = max(int(canvas_width), 10)
        canvas_height = max(int(canvas_height), 10)

        img = Image.new("RGBA", (int(canvas_width), int(canvas_height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 4) 全局背景
        if template.bg_color:
            try:
                draw.rounded_rectangle([0, 0, canvas_width, canvas_height],
                                       radius=template.bg_radius, fill=template.bg_color)
            except Exception:
                draw.rectangle([0, 0, canvas_width, canvas_height], fill=template.bg_color)

        # 5) 关键字正则
        keyword_pattern = None
        if template.keywords:
            keyword_pattern = re.compile(f"({'|'.join(map(re.escape, template.keywords))})", re.IGNORECASE)

        # 6) 按行绘制（支持关键词与单词间距 & 投影/3D）
        y_cursor = (canvas_height - total_text_height) / 2
        for line in lines:
            line_width = measure_line_width(line)
            x_cursor_start = (canvas_width - line_width) / 2
            x_cursor = x_cursor_start

            tokens = re.findall(r'\s+|[^\s]+', line)

            for idx, token in enumerate(tokens):
                is_space = token.isspace()
                is_keyword = (not is_space) and (token.strip().lower() in keyword_set)

                if is_keyword:
                    text_color = template.keyword_text_color if template.keyword_text_color else template.base_color
                    stroke_w = template.keyword_stroke_width if template.keyword_stroke_width is not None else template.stroke_width
                    stroke_c = template.keyword_stroke_color if template.keyword_stroke_color else template.stroke_color
                else:
                    text_color = template.base_color
                    stroke_w = template.stroke_width
                    stroke_c = template.stroke_color

                # 关键词背景（仅非空白 token）
                if is_keyword and template.keyword_bg_color:
                    try:
                        bbox = font.getbbox(token)
                        bg_coords = [
                            x_cursor + bbox[0] - template.keyword_bg_padding_x,
                            y_cursor + bbox[1] - template.keyword_bg_padding_y,
                            x_cursor + bbox[2] + template.keyword_bg_padding_x,
                            y_cursor + bbox[3] + template.keyword_bg_padding_y
                        ]
                        ImageDraw.Draw(img).rectangle(bg_coords, fill=template.keyword_bg_color)
                    except Exception:
                        w, h = draw.textsize(token, font=font)
                        bg_coords = [
                            x_cursor - template.keyword_bg_padding_x,
                            y_cursor - template.keyword_bg_padding_y,
                            x_cursor + w + template.keyword_bg_padding_x,
                            y_cursor + h + template.keyword_bg_padding_y
                        ]
                        ImageDraw.Draw(img).rectangle(bg_coords, fill=template.keyword_bg_color)

                # ---- 阴影处理（先画阴影，再画正文字）----
                # 3D 挤出阴影优先
                if template.is_3d_shadow and template.shadow_layers > 0:
                    green_shadow = template.stroke_color  # 使用绿色描边作为 3D 阴影颜色

                    for i in range(template.shadow_layers):
                        ox = template.shadow_step[0] * (i + 1)
                        oy = template.shadow_step[1] * (i + 1)

                        draw.text(
                            (x_cursor + ox, y_cursor + oy),
                            token,
                            font=font,
                            fill=green_shadow,          # 绿色 3D 阴影层
                            stroke_width=0,             # 3D 阴影本身不再描边
                            stroke_fill=None
        )
                # 普通投影（drop shadow）
                elif template.enable_drop_shadow and template.drop_shadow_color:
                    shadow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
                    shadow_draw = ImageDraw.Draw(shadow_img)
                    sx = x_cursor + template.drop_shadow_offset[0]
                    sy = y_cursor + template.drop_shadow_offset[1]
                    shadow_draw.text((sx, sy), token, font=font, fill=template.drop_shadow_color)
                    if template.drop_shadow_blur and template.drop_shadow_blur > 0:
                        try:
                            blurred = shadow_img.filter(ImageFilter.GaussianBlur(template.drop_shadow_blur))
                            img.paste(blurred, (0, 0), blurred)
                        except Exception:
                            img.paste(shadow_img, (0, 0), shadow_img)
                    else:
                        img.paste(shadow_img, (0, 0), shadow_img)

                # ---- 正文字（含描边）----
                try:
                    draw.text((x_cursor, y_cursor), token, font=font, fill=text_color,
                              stroke_width=stroke_w, stroke_fill=stroke_c)
                except TypeError:
                    draw.text((x_cursor, y_cursor), token, font=font, fill=text_color)

                # 前进光标
                advance = font.getlength(token)
                if is_space and template.word_spacing_px > 0:
                    advance += template.word_spacing_px
                x_cursor += advance

            y_cursor += line_height

        return np.array(img)


下述是我的字幕配置代码
# subtitle_style_config.py

from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Dict, Any

# ==============================================================================
#  1. 全局语言配置
# ==============================================================================
GLOBAL_FONT_TO_LANGUAGES: Dict[str, List[str]] = {
    "NotoSansArabic-Bold.ttf":[
        "en"
    ],
    "SourceHanSans.ttc": [
        "zh", "zh-cn", "zh-tw", "zh-hk", # 中文 (简体, 繁体, 香港)
        "ja", "ja-jp",                 # 日语
        "ko", "ko-kr"                  # 韩语
    ],
    "NotoSansArabic-Bold.ttf": [
        "ar",   # 阿拉伯语
        "fa",   # 波斯语
        "ur"    # 乌尔都语
    ],
    "arial.ttf": [
        "en-us", "en-gb", # 英语
        "fr", "fr-fr",          # 法语
        "de", "de-de",          # 德语
        "es", "es-es",          # 西班牙语
        "it", "it-it",          # 意大利语
        "pt", "pt-pt",          # 葡萄牙语
        "ru", "ru-ru",          # 俄语
        "uk", "uk-ua",          # 乌克兰语
        "bg",                   # 保加利亚语
        "sr",                   # 塞尔维亚语
        "el",                   # 希腊语
        "vi",                   # 越南语
        "th",                   # 泰语
        # ... 可以继续添加使用拉丁或西里尔字母的语言
    ]
}

# 当语言在清单中找不到时，使用的默认字体
DEFAULT_FONT = "NotoSans-Bold.ttf"

def get_font_for_language(language: str,
                          template_font_map: Optional[Dict[str, str]] = None,
                          fallback_font_name: Optional[str] = None) -> str:
    """
    按优先级选择字体：
    1) 模板级 font_map（精确匹配，其次主语言匹配）
    2) 全局 GLOBAL_FONT_TO_LANGUAGES
    3) fallback_font_name（通常为模板的 font_name）
    4) DEFAULT_FONT
    """
    if not language:
        return fallback_font_name or DEFAULT_FONT

    lang_norm = language.lower().strip()

    # 1) 模板级映射
    if template_font_map:
        # 先 exact（不区分大小写），再 base-lang
        # exact
        for k, v in template_font_map.items():
            if lang_norm == k.lower():
                return v
        # base-lang
        if '-' in lang_norm:
            base = lang_norm.split('-')[0]
            # 先 exact base；再尝试把 map 的 key 也拆 base 比较
            for k, v in template_font_map.items():
                if base == k.lower():
                    return v
            for k, v in template_font_map.items():
                k_base = k.lower().split('-')[0]
                if base == k_base:
                    return v

    # 2) 全局映射
    for font, langs in GLOBAL_FONT_TO_LANGUAGES.items():
        langs_lower = [x.lower() for x in langs]
        if lang_norm in langs_lower:
            return font
    if '-' in lang_norm:
        base = lang_norm.split('-')[0]
        for font, langs in GLOBAL_FONT_TO_LANGUAGES.items():
            langs_lower = [x.lower() for x in langs]
            if base in langs_lower:
                return font

    # 3) fallback → 4) 默认
    return fallback_font_name or DEFAULT_FONT

@dataclass
class SubtitleTemplate:
    """
    定义一个完整的字幕样式配置。
    这个数据类代表了所有可用样式属性的集合，是最终应用到渲染逻辑中的形态。
    """
    # --- 字体与文本基础样式 ---
    font_name: str                              # 字体文件名 (例如: "arial.ttf", "SourceHanSans.ttc")
    font_size: int                              # 字体大小，单位为像素 (px)
    base_color: Tuple[int, int, int, int]       # 普通文字颜色，格式为 (R, G, B, A)，A为透明度 (0-255)
    font_style: str = "normal"                  # 字体样式: "normal" (普通), "bold" (粗体), "italic" (斜体)
    opacity: float = 1.0                        # 字幕整体透明度 (1.0为完全不透明, 0.0为完全透明)
    letter_spacing: int = 0                     # 字符间距，单位为像素
    line_spacing: int = 0                       # 行间距，单位为像素
    word_spacing_px: int = 0                    # --- 新增：单词间距（仅英文等按词分行语言有效），单位像素 ---
    font_map: Optional[Dict[str, str]] = None   # --- 新增：模板级语言→字体映射（优先级最高） ---

    # --- 描边样式 ---
    stroke_color: Optional[Tuple[int, int, int, int]] = None  # 描边颜色 (R, G, B, A)
    stroke_width: int = 0                                     # 描边宽度，单位为像素

    # --- 投影（drop shadow）新配置 ---
    enable_drop_shadow: bool = False   
    drop_shadow_color: Optional[Tuple[int, int, int, int]] = None  # 阴影颜色含透明度
    drop_shadow_offset: Tuple[int, int] = (0, 0)  # 阴影偏移（x, y）
    drop_shadow_blur: int = 0  # 高斯模糊半径

    # --- 阴影样式 ---
    shadow_color: Optional[Tuple[int, int, int, int]] = None  # 阴影颜色 (R, G, B, A)
    shadow_offset: Tuple[int, int] = (0, 0)  # 阴影偏移 (水平x, 垂直y)，单位为像素
    shadow_blur: int = 0  # 阴影模糊半径

    # --- 全局背景样式 (作用于所有字幕) ---
    bg_color: Optional[Tuple[int, int, int, int]] = None  # 背景颜色 (R, G, B, A)
    bg_padding_x: int = 0  # 背景左右内边距(字幕距离背景左右的距离)
    bg_padding_y: int = 0  # 背景上下内边距(字幕距离背景上下的距离)
    bg_radius: int = 8  # 背景圆角半径 (0为直角)
    bg_border_color: Optional[Tuple[int, int, int, int]] = None  # 背景边框颜色 (R, G, B, A)
    bg_border_width: int = 0  # 背景边框宽度
    bg_max_width: Optional[int] = None  # 背景最大宽度，超出则换行

    # --- 布局与定位 ---
    writing_mode: str = "horizontal"  # 文本书写模式: "horizontal" (横排), "vertical" (竖排)

    # --- 关键词特殊样式 (用于覆盖基础样式) ---
    # --- 高亮样式 (用于覆盖基础样式) ---
    highlight_text_color: Optional[Tuple[int, int, int, int]] = None       # 高亮文字颜色
    highlight_bg_color: Optional[Tuple[int, int, int, int]] = None         # 高亮背景颜色
    highlight_stroke_color: Optional[Tuple[int, int, int, int]] = None     # 高亮描边颜色
    highlight_stroke_width: Optional[int] = None                           # 高亮描边宽度
    highlight_font_style: Optional[str] = None                             # 高亮字体样式
    highlight_bg_padding_x: int = 0                                        # 高亮背景左右内边距
    highlight_bg_padding_y: int = 0                                        # 高亮背景上下内边距

    # --- 3D阴影样式 ---
    is_3d_shadow: bool = False          # 是否启用3D阴影效果
    shadow_layers: int = 5              # 3D阴影层数（默认5层）
    shadow_step: Tuple[int, int] = (2, 2)  # 每层阴影的步进偏移量

# ==============================================================================
# 1. 基础模板：定义所有属性的默认值 (Single Source of Truth)
#    这是所有自定义模板的基础，修改这里会影响所有未指定该属性的模板。
# ==============================================================================
DEFAULT_TEMPLATE = SubtitleTemplate(
    font_name="SourceHanSansCN-Normal",                 # 默认字体为 Arial
    font_size=32,                          # 默认字号为 32px
    base_color=(255, 255, 255, 255),       # 默认文字颜色为纯白色
    stroke_color=(0, 0, 0, 200),           # 默认带有轻微的半透明黑色描边，以增强在各种背景下的可读性
    stroke_width=0,                        # 默认描边宽度为 2px
    line_spacing=0,                        # 默认行间距为 5px
    word_spacing_px=0,
    # 所有其他未在此处指定的属性，都将使用上面 SubtitleTemplate dataclass 中定义的默认值。
)

# ==============================================================================
# 2. 样式库：现在只包含“客制化”的覆盖属性 (简洁、清晰)
#    这里的每一项都是一个字典，只定义与 DEFAULT_TEMPLATE 不同的地方。
# ==============================================================================
STYLE_LIBRARY: Dict[str, Dict[str, Any]] = {
    # "默认" 样式，它直接使用基础模板，因此客制化部分为空字典。
    "default": {},
    
    # 经典黑条：白字 + 黑底。
    "classic_black": {
        "font_size": 32,
        "stroke_width": 0,
        "bg_color": (0, 0, 0, 220),
        "bg_radius": 0,
        "bg_padding_x": 10, # 背景左右内边距(字幕距离背景左右的距离)
        "bg_padding_y": 8, # 背景上下内边距(字幕距离背景上下的距离)
        "word_spacing_px": 5,
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }
    },

    # 经典白条：黑字 + 圆角白底
    "classic_white": {
        "font_size": 32,
        "base_color": (0, 0, 0, 255),
        "stroke_width": 0,
        "bg_color": (255, 255, 255, 255),
        "bg_padding_x": 10,
        "bg_padding_y": 8,
        "bg_radius": 8,
        "word_spacing_px": 5,
        "line_spacing": 15,
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }
    },
    
    # 边框：白字 + 黑色描边，无背景
    "border": {
        "font_size": 32,
        "base_color": (255, 255, 255, 255),
        "stroke_color": (0, 0, 0, 255),
        "stroke_width": 4,
        "shadow_color": (0, 0, 0, 180),
        "word_spacing_px": 5,
        "line_spacing": 15,
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }
    },

    # 轮廓高亮：字幕轮廓黑色，基础文字白色，关键词青色
    "outline_highlight": {
		"render_mode": "word_highlight",
        "font_size": 32,
        "base_color": (255, 255, 255, 255),
        "stroke_color": (0, 0, 0, 255),
        "stroke_width": 3,
        "word_spacing_px": 5,
        "highlight_text_color": (0, 255, 170, 255),
        "highlight_stroke_color": (0, 0, 0, 255),
        "line_spacing": 15,
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }
    },

    # 区块强调 字体黄色，无描边，关键词黑色背景
    "block_highlight": {
		"render_mode": "word_highlight",
        "font_size": 32,
        "base_color": (255, 255, 0, 255),
        "stroke_width": 0,
        "highlight_text_color": (255, 255, 0, 255),
        "highlight_bg_color": (0, 0, 0, 255), 
        "highlight_bg_padding_y": 10,
        "enable_drop_shadow": True,
        "drop_shadow_color": (0, 0, 0, 200),
        "drop_shadow_offset": (2, 4),
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }
    },

    # 半透明 白色文字 黄色关键词 灰白色背景
    "semi_transparent": {
		"render_mode": "word_highlight",
        "font_size": 20,
        "base_color": (255, 255, 255, 255),
        "highlight_text_color": (255, 255, 0, 255),
        "highlight_bg_color": (0, 0, 0, 180),
        "bg_color": (0, 0, 0, 180),
        "bg_radius": 8,
        "bg_padding_x": 10,
        "bg_padding_y": 8,
        "word_spacing_px": 5, # 单词间距
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }
    },

    # 黑暗 白色文字 绿色关键词 黑色背景
    "dark": {
        "font_size": 20,
        "base_color": (255, 255, 255, 255),
        "highlight_text_color": (0, 255, 0, 255),
        "highlight_bg_color": (0, 0, 0, 255),
        "bg_color": (0, 0, 0, 255),
        "bg_radius": 8,
        "word_spacing_px": 5, # 单词间距
        "bg_padding_x": 10,
        "bg_padding_y": 8,
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }
    },

    # 清新 白色文字 绿色关键词 白色背景
    "fresh": {
		"render_mode": "word_highlight",
        "font_size": 32,
        "base_color": (255, 255, 255, 255),
        "highlight_text_color": (84, 255, 159, 255),
        "word_spacing_px": 5, # 单词间距    
        # 开启投影（柔和）
        "enable_drop_shadow": True,
        "drop_shadow_color": (0, 0, 0, 200),
        "drop_shadow_offset": (2, 4),
        "drop_shadow_blur": 5,
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        },            
    },

    # 白条式高亮 黑色文字 蓝色关键词 白色背景
    "white_highlight": {
        "font_size": 20,
        "base_color": (0, 0, 0, 255),
        "bg_color": (255, 255, 255, 255),
        "highlight_text_color": (56, 30, 215, 255),
        "bg_padding_x": 10,
        "bg_padding_y": 8,
        "drop_shadow_blur": 5,
        "word_spacing_px": 5,
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }
    },

    # 柠檬 ：黄色字体
    "lemon": {
        "font_size": 20,
        "drop_shadow_blur": 5,
        "base_color": (255, 255, 0, 255),
        # 开启投影（柔和）
        "enable_drop_shadow": True,
        "drop_shadow_color": (0, 0, 0, 200),
        "drop_shadow_offset": (2, 4),
        "drop_shadow_blur": 5,
        # 描边
        "stroke_color": (0, 0, 0, 255),
        "stroke_width": 2,
        # 字间距
        "word_spacing_px": 5,
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }        
    },

    # 倾斜：白色字体，带有黑色描边和阴影（模仿图片效果）
    "italic": {
        "font_size": 36,
        "base_color": (255, 255, 255, 255), # **文字颜色：白色**
        "stroke_color": (0, 0, 0, 255),
        "stroke_width": 2,
        # 开启投影（柔和）
        "enable_drop_shadow": True,
        "drop_shadow_color": (0, 0, 0, 200),
        "drop_shadow_offset": (2, 4),
        "drop_shadow_blur": 5,
        # 描边
        "stroke_color": (0, 0, 0, 255),
        "stroke_width": 2,
        # 字间距
        "line_spacing": 15,        
        "word_spacing_px": 5,
        "font_map": {
            "en": "Rubik-BoldItalic.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }         
    },

    # 阴影区块强调 白色字体 白色关键词 粉色背景
    "shadow_block_highlight": {
        "font_size": 20,
        "base_color": (255, 255, 255, 255),
        "highlight_text_color": (255, 255, 255, 255),
        "highlight_bg_color": (210, 144, 243, 255),
        # 开启投影（柔和）
        "enable_drop_shadow": True,
        "drop_shadow_color": (0, 0, 0, 200),
        "drop_shadow_offset": (2, 4),
        "drop_shadow_blur": 5,
        "line_spacing": 15,        
        # 关键词上下距离
        "highlight_bg_padding_y": 8,
        # 字间距
        "word_spacing_px": 5,
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }  
    },

    # 霓虹
    "neon": {
        "font_size": 20,
        "shadow_offset": (0, 0),
        "base_color": (247, 148, 227, 255),             # 文本颜色设置为亮粉色 (Hot Pink)**
        "shadow_color": (255, 105, 180, 255),           # 阴影颜色设置为亮粉色 (Hot Pink)** 
        "shadow_blur": 10,
        # 开启投影（柔和）
        "enable_drop_shadow": True,
        "drop_shadow_color": (0, 0, 0, 200),
        "drop_shadow_offset": (2, 4),
        "drop_shadow_blur": 5,
        # 字间距
        "word_spacing_px": 5,
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }             
    },

    # 3D 阴影
    "3d_shadow": {
        "font_size": 20,
        "base_color": (0, 0, 0, 255),   # 黑色主文字
        "stroke_color": (100, 232, 123, 255),       # 绿色
        "stroke_width": 2,
        "is_3d_shadow": True,                 # 启用3D效果
        "shadow_layers": 3,                   # 8层阴影，立体感更强
        "shadow_step": [0, 2],                # 每层向右下偏移3像素
        "shadow_blur": 0,                     # 3D效果不需要模糊
        # 字间距
        "word_spacing_px": 5,
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }
    },

    # 白色轮廓 ：白色轮廓 黑色字体
    "white_outline": {
        "font_size": 20,
        "base_color": (0, 0, 0, 255),
        "stroke_color": (255, 255, 255, 255),
        "stroke_width": 3,
        # 字间距
        "word_spacing_px": 5,
        "line_spacing": 15,        
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }  
    },

    # 聚光灯区块强调 白色字体 黄色关键词 白色背景
    "spotlight_block_highlight": {
        "font_size": 20,
        "base_color": (255, 255, 255, 255),
        "highlight_text_color": (0, 0, 0, 255),
        "highlight_bg_color": (52, 241, 139, 255),
        "highlight_bg_padding_y": 10,
        "line_spacing": 15,
        # 字间距
        "word_spacing_px": 5,
        "font_map": {
            "en": "Rubik-Bold.ttf",
            "zh-CN": "SourceHanSansCN-Bold.otf",
            "thai":"NotoSansThai-Bold.ttf",
            "arabic": "NotoSansArabic-Bold.ttf"
        }  
    },
}

字幕位置配置
# 字幕位置配置
# subtitle_position_config.py
from typing import Dict, Any

VIDEO_SPEC_CONFIG: Dict[str, Dict[str, Any]] = {
    "9:16": {
        "layout_config": {
            "bottom": {  # 字幕位置：bottom
                "position_x": "center",  # 水平位置: "left", "center", "right"
                "position_y": "bottom",  # 垂直位置: "top", "center", "bottom"
                "offset_x": 0,  # 水平偏移量，正值向右，负值向左
                "offset_y": 250,  # bottom时 垂直偏移量，负值向下，正值向上
                "line_spacing": 0,  # 行间距 (单位：像素)
                "default_max_lines": 2, # 每个视频最多显示2行字幕
                "default_max_chars_per_line": 30,
            },
            "top": {  # 字幕位置：top
                "position_x": "center",
                "position_y": "top",
                "offset_x": 0,
                "offset_y": 100, # top 时，垂直偏移量，正值向下，负值向上
                "line_spacing": 2,
                "default_max_lines": 2,
                "default_max_chars_per_line": 35,
            },
            "center": {  # 字幕位置：center
                "position_x": "center",
                "position_y": "center",
                "offset_x": 0,
                "offset_y": 0,
                "max_lines": 2,
                "default_max_chars_per_line": 35,
                "line_spacing": 2,
            },
        },
        "line_break_rules": {
            "zh-CN": {"max_chars_per_line": 20, "max_lines": 2},  # 中文：每行最多15个字符，最多2行
            "en": {"max_chars_per_line": 20, "max_lines": 2},  # 英文：每行最多35个字符，最多2行
        }
    },

    "default_ratio": {
        "layout_config": {
            "bottom": {
                "position_x": "center",
                "position_y": "bottom",
                "offset_x": 0,
                "offset_y": 0,
                "max_lines": 2,
                "default_max_chars_per_line": 25,
                "line_spacing": 3,
            },
            "top": {
                "position_x": "center",
                "position_y": "top",
                "offset_x": 0,
                "offset_y": 0,
                "max_lines": 3,
                "default_max_chars_per_line": 25,
                "line_spacing": 3,
            },
            "center": {
                "position_x": "center",
                "position_y": "center",
                "offset_x": 0,
                "offset_y": 0,
                "default_max_lines": 2,
                "default_max_chars_per_line": 25,
                "line_spacing": 3,
            },
        },
        "line_break_rules": {
            "zh-CN": {"max_chars_per_line": 12, "max_lines": 2},  # 中文
            "en": {"max_chars_per_line": 25, "max_lines": 2},  # 英文
            "ja": {"max_chars_per_line": 20, "max_lines": 2},  # 日文
            "ko": {"max_chars_per_line": 20, "max_lines": 2},  # 韩语
        }
    },
}

其中json字幕文件中的内容为
{
    "input_path": "/home/zhanglingwen/Algorithm/business-algo/data/output/htdemucs/input_extracted_audio/vocals.wav",
    "is_video": false,
    "language": "zh",
    "speaker_diarization_enabled": false,
    "text": "听说他不韬光掩晦改做搭桥牵线了,迪夫希克无视断供芯片了",
    "sentences": [
        {
            "index": 1,
            "start": 9.47,
            "end": 14.15,
            "text": "听说他不韬光掩晦改做搭桥牵线了",
            "words": [
                {
                    "word": "听说",
                    "start": 9470,
                    "end": 10030
                },
                {
                    "word": "他",
                    "start": 10070,
                    "end": 10525
                },
                {
                    "word": "不",
                    "start": 11310,
                    "end": 11490
                },
                {
                    "word": "韬光",
                    "start": 11490,
                    "end": 11870
                },
                {
                    "word": "掩晦",
                    "start": 11890,
                    "end": 12350
                },
                {
                    "word": "改",
                    "start": 12450,
                    "end": 12690
                },
                {
                    "word": "做",
                    "start": 12710,
                    "end": 12950
                },
                {
                    "word": "搭桥牵线",
                    "start": 12970,
                    "end": 13850
                },
                {
                    "word": "了",
                    "start": 13910,
                    "end": 14150
                }
            ]
        },
        {
            "index": 2,
            "start": 14.51,
            "end": 17.37,
            "text": "迪夫希克无视断供芯片了",
            "words": [
                {
                    "word": "迪夫",
                    "start": 14510,
                    "end": 15050
                },
                {
                    "word": "希克",
                    "start": 15050,
                    "end": 15470
                },
                {
                    "word": "无视",
                    "start": 15490,
                    "end": 15930
                },
                {
                    "word": "断供",
                    "start": 16050,
                    "end": 16570
                },
                {
                    "word": "芯片",
                    "start": 16570,
                    "end": 17010
                },
                {
                    "word": "了",
                    "start": 17130,
                    "end": 17370
                }
            ]
        }
    ]
}

现在我需要你基于我的现有的代码帮我完成一个需求
模版中如果有高亮相关的这个参数配置，逐词时间戳或单条字幕时间戳你可以从这个
json中获取到
模版中如：
        "highlight_text_color": (0, 255, 170, 255),
        "highlight_stroke_color": (0, 0, 0, 255),
		或：
        "highlight_text_color": (255, 255, 0, 255),
        "highlight_bg_color": (0, 0, 0, 255), 
        "highlight_bg_padding_y": 10,
这些需要高亮的(逐词高亮)，一个单词，或一个中文字符这种样式，就像歌词那种，
变化，比如一个字幕是This is another line with some text.
那么开始This 变成关键词样式，然后is 变成关键词样式, This 恢复原来的样式
但还是现在我的代码，绘制不上去，没有达到我要的效果，请帮我解决

