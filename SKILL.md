---
name: focusmedia-image-gen
description: Generate Focus Media / 分众传媒 framed-media demos, realistic elevator/lobby environment images, exact LCD lower-strip creatives, and framed LCD TVC demos. Use for 分众传媒 demo 图、带框图、环境图、人群效果图、电梯电视/LCD/楼宇 LCD、智能屏、海报框架，或将创意安装进分众媒体实景。
---

# Focus Media Image Generation

把用户提供的海报、KV 或 TVC 画面，生成媒体框体正确、环境比例可信的分众传媒效果图。

默认交付两张图：

1. 无环境的带框媒体演示图
2. 同一媒体安装进真实比例电梯厅或轿厢的环境效果图

带框图先使用已验证的完整标准框体；环境图先锁定真实参考图的空间，再完成受光、透视和安装关系的融合。

## Reference Loading

- 读取 `references/media-specs.md`，确认媒介名称、尺寸和比例。
- 涉及带框图、LCD 上下屏、标准框体或替换既有广告内容时，读取 `references/frame-first-workflow.md`。
- 涉及环境、人群或比例时，读取 `references/spatial-parameters.md` 和 `references/visual-rules.md`。
- 生成或修改图片前，读取 `references/generation-guide.md`。
- 涉及 LCD 下屏或带框 LCD TVC 时，读取 `references/lcd-strip-and-tvc-workflow.md`。
- 环境图必须先从阿里云参考图库选择并下载真实参考图：

```bash
scripts/select_media_references.py --media lcd --tag elevator-hall --limit 3
scripts/fetch_reference_images.py --media lcd --limit 2
```

`fetch_reference_images.py` 会自动从 156 张已分级的远端参考图库中筛选并下载通过校验的图片到 `.focusmedia-cache/references/`。其中 58 张是默认主力参考；98 张场景参考覆盖宏大空间、人物尺度、多海报同框、轿厢内与特殊视角。暗沉、老旧、杂乱或明显拉低媒介质感的环境图已排除。试用者不需要服务器账号、SSH key 或 API key。Git 包只保留 16 张精选缩略参考图供快速离线查看，其余图片按需从阿里云获取。

默认选择主力参考；有明确画面意图时按用途调用场景参考，例如：

```bash
scripts/select_media_references.py --media lcd --tier scenario --use-case wide-impact --limit 3
scripts/select_media_references.py --media poster --tier scenario --use-case multi-frame-poster-coverage --limit 3
scripts/select_media_references.py --media smart --tier scenario --use-case people-scale --limit 2
```

## Verified Framed Standards

以下三类无环境带框图已经有完整、验证过的标准框体，必须保留完整外框，只替换广告展示面：

| 媒介 | 标准文件 | 可替换区域 |
| --- | --- | --- |
| 32 英寸智能屏 | `assets/framed-demo-standards/smart-32-standard.png` | 单块 9:16 竖屏展示面 |
| 32 英寸楼宇 LCD | `assets/framed-demo-standards/lcd-32-standard.png` | 上屏和下屏 |
| 海报框架 | `assets/framed-demo-standards/poster-frame-standard.png` | 玻璃后的纸质海报区域 |

如果用户要求的带框产品演示图没有对应标准框体，停止并取得直接产品演示源或新增获批标准；不得从环境照片裁出设备后冒充标准框体。

智能屏的标准口径为 32 英寸。当前公开包只提供这一种经过验证的智能屏完整框体；其他尺寸不能作为已验证带框图交付。

## Core Rules

- 将用户输入归类为：精确屏幕/海报创意、完整设计板、待生成创意，或既有带框/环境图。
- 将输出归类为：带框产品演示图、无人环境图、带人环境图，或安装修改图。
- 环境图的真实参考照片是空间、透视、灯光和比例的唯一依据；标准带框图只作为硬件身份参考。最终环境图不得使用平面贴图作为成品。
- 当真实参考照片已有正确媒介硬件时，优先执行屏幕/海报区域替换；设备边界、安装深度、反射、白框或黑色边框保持不变。
- LCD 必须是白色横向机身、上方 16:9 主屏、窄下屏以及中部品牌/传感器带。下屏不能变成第二块完整高度的屏幕。
- 海报框应保持白色或铝色框体与玻璃反光，画面保持纸质印刷感，不能变成发光屏。
- 智能屏只替换点亮的显示像素；保留黑色机身、边框、传感器、标识、安装深度和反射。
- 同一楼层内可见的多台 LCD 在同一拍摄时刻必须显示相同的上屏和下屏广告。一次编辑导致硬件、角度或建筑变化时，回退并按设备逐个修改。
- 环境里保持电梯门、呼梯按钮、扶手、墙缝、地面、天花和人物尺度。媒体作为后装设备，不能为了容纳媒体而改变空间。
- LCD 相对门宽和按钮高度可测量时，运行 `scripts/validate_media_scale.py`；不通过则不能交付。
- 每一轮修改都回到原始真实参考图，合并所有仍有效的要求再生成。不得在被拒绝的位图上连续叠加编辑。

## Exact LCD Workflows

### LCD 下屏

下屏创意必须是精确 `16:3`。用双保护带生成和裁切，避免模型返回近似超宽比例：

```bash
scripts/prepare_lcd_lower_band.py template \
  --canvas 1536x1024 \
  --guide lower-band-guide.png \
  --mask lower-band-mask.png \
  --manifest lower-band-manifest.json

scripts/prepare_lcd_lower_band.py crop \
  --input returned.png \
  --output lower-1920x360.png \
  --report lower-crop-report.json
```

禁止用默认左右扩图来修补比例漂移；重要内容必须留在内层安全区。

### 干净 LCD 带框图

```bash
scripts/composite_lcd_screens.py \
  --main main-1920x1080.png \
  --lower lower-1920x360.png \
  --output framed-lcd.png
```

该脚本只改变标准 LCD 模板的上屏和下屏区域。

### 带框 LCD TVC

正式 TVC 演示图保持完整标准框体和静态下屏。源视频必须先确认是 `4:3` 或 `16:9`；上屏在准确帧上切换到已批准尾帧，音频通过复制或一次受控 AAC 转码保留：

```bash
scripts/compose_lcd_tvc_demo.py \
  --source source.mp4 \
  --tail approved-tail-1920x1080.png \
  --lower approved-lower-1920x360.png \
  --switch-time 14.12 \
  --output framed-demo.mp4 \
  --contact-sheet framed-demo-contact-sheet.png \
  --report framed-demo-report.json
```

交付前检查导出的 contact sheet 和 report。

## Environment Integration

选择并下载匹配媒介、场景和人物状态的真实参考图后：

1. 锁定相机位置、可见表面、电梯门宽、按钮、扶手、墙面、地面和人物。
2. 准备与目标媒介比例一致的广告创意和带框标准作为身份参考。
3. 用图像编辑能力将媒介安装到真实墙面或替换既有展示面。
4. 匹配墙面透视、消失线、局部光色、反射、接触阴影、曝光、清晰度和景深。
5. 逐项检查媒介类型、框体边界、屏幕比例、按钮可达性和环境尺度。

如果模型改变了非目标设备、媒体类型、建筑结构或人物锚点，丢弃该结果，从原始参考图重新执行目标区域编辑。

## Output Check

交付前确认：

- 用户请求的媒介类型和已用的标准框体一致。
- 带框产品演示图使用完整标准框体，而非环境图裁切或重新生成的外壳。
- 环境图使用了已下载的真实参考图，且最终媒介具有正确的透视、安装深度、反射和阴影。
- LCD 上下屏比例正确，白色机身仍清晰可辨。
- 多 LCD 场景的同层广告播放同步。
- 海报框保有纸质和玻璃特征；智能屏保有黑色硬件特征。
- 文字、二维码和极小 Logo 若需生产级精确度，最后以专业透视与光照合成回贴。

## Package Layout

- `assets/framed-demo-standards/`：随 Skill 分发的三套验证标准框体。
- `assets/reference-thumbnails/`：随 Skill 分发的 16 张精选参考缩略图。
- `references/curated-reference-library.json`：主力、场景与排除规则的唯一配置清单。
- `references/remote-manifest.json`：156 张阿里云只读参考图的可筛选清单、用途标签与 checksum。
- `scripts/fetch_reference_images.py`：自动下载和校验参考图。
- `.focusmedia-cache/references/`：按需下载的本地缓存，不纳入 Git。
- `requirements.txt`：图片处理依赖；TVC 合成另需本机安装 `ffmpeg` 和 `ffprobe`。
