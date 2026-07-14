# 小说网文图片生成 Prompt 模板库

> **加载时机**：Agent 需要为小说生成角色图、场景图或封面图时加载此文件。
> **版本**：v1.0 | 最后更新：2026-07-14

---

## 使用说明

本文件提供适用于网文创作的图片生成 prompt 模板，覆盖角色、场景、封面三大类别。根据用户配置的图片模型（DALL-E 3 / Midjourney / Stable Diffusion），每个模板均给出**中文意图描述**、**可直接使用的英文 prompt**，以及**参数建议**。

### 通用规则

1. **优先读取用户配置**的模型类型、画风偏好、分辨率等参数。
2. **替换 `{}` 占位符**：模板中用 `{name}`、`{scene}` 等标记的部分，需根据小说实际内容替换。
3. **保持风格一致**：同一部小说的所有图片应使用统一的画风关键词（如 `Chinese ink wash painting style`、`anime style`、`semi-realistic illustration`）。
4. **参数仅作参考**，实际生成时应根据模型版本调整。

---

## 1. 角色图模板

### 1.1 男性主角

#### 玄幻/仙侠男主

**中文意图**：一位年轻的修仙者，身着白色道袍，背负长剑，立于悬崖之巅，周身环绕淡蓝色灵力光芒，面容冷峻，长发飘逸。

```
A young Chinese cultivator, handsome male, wearing flowing white Daoist robes,
long black hair flowing in the wind, a spiritual sword on his back,
standing on a cliff edge overlooking misty mountains,
subtle blue spiritual energy glowing around his body,
cold and sharp facial expression, sharp eyes,
fantasy xianxia atmosphere, epic composition,
semi-realistic illustration, detailed fabric, dramatic lighting
```

**MJ 参数**：`--ar 2:3 --style raw --s 250 --v 6.1`
**SD 参数**：`Steps: 30, Sampler: DPM++ 2M Karras, CFG scale: 7, Negative: ugly, deformed, blurry, low quality, extra fingers, bad anatomy`
**DALL-E 3**：直接使用中文描述生成，画质 `standard` 或 `hd`

---

#### 都市男主

**中文意图**：霸道总裁，黑色西装，站在落地窗前俯瞰城市夜景，单手插兜，神情自信而略带玩味。

```
A handsome Chinese businessman, tall and fit, wearing a perfectly tailored black suit,
white shirt slightly unbuttoned at the collar, one hand in pocket,
standing in front of a floor-to-ceiling window with city nightscape backdrop,
confident smirk, sharp jawline, intense gaze,
modern urban atmosphere, cinematic lighting, 8K, photorealistic
```

**MJ 参数**：`--ar 2:3 --style raw --s 200`
**SD 参数**：同上通用参数
**DALL-E 3**：可直接用中文描述，并追加 `写实摄影风格，电影级光影`

---

#### 历史/古风男主

**中文意图**：一位少年将军，身着明光铠，手持长枪，骑在黑色战马上，背景是烽火战场，眼神坚毅。

```
A young Chinese general, handsome but battle-worn, wearing Tang Dynasty armor (mingguang armor),
holding a long spear, riding a black warhorse, galloping through a battlefield,
smoke and fire in the background, determined and heroic expression,
historical fantasy, epic battle scene, dramatic sky,
traditional Chinese painting influence, rich colors, detailed armor
```

**MJ 参数**：`--ar 16:9 --style raw --s 300`
**SD 参数**：同上

---

### 1.2 女性主角

#### 仙侠/玄幻女主

**中文意图**：一位仙气飘飘的女修，身着青色纱裙，手持白玉笛子，站在桃花树下，周身飘散着花瓣与淡淡灵光。

```
A beautiful Chinese female cultivator, elegant and ethereal,
wearing flowing cyan silk robes with translucent sleeves,
holding a white jade flute, standing under a blooming peach blossom tree,
pink petals floating in the air, soft spiritual glow around her,
gentle yet otherworldly expression, long black hair adorned with simple hairpins,
Chinese xianxia style, soft focus, dreamy atmosphere, detailed fabric
```

**MJ 参数**：`--ar 2:3 --style raw --s 250`
**SD 参数**：`Steps: 30, Sampler: DPM++ 2M Karras, CFG scale: 7, Negative: ugly, deformed, extra limbs, bad hands, blurry`

---

#### 都市女主

**中文意图**：干练的都市白领女性，米色风衣，内搭白色衬衫，手拿咖啡走在繁华商业街上，阳光正好。

```
A stylish Chinese woman, confident and sophisticated,
wearing a beige trench coat over a white blouse, holding a coffee cup,
walking on a bustling modern city street, golden hour sunlight,
natural makeup, medium-length dark hair, looking slightly to the side with a gentle smile,
photorealistic, fashion editorial style, shallow depth of field, 8K
```

**MJ 参数**：`--ar 2:3 --s 180`
**SD 参数**：同上

---

#### 古代/宫廷女主

**中文意图**：一位身着华丽宫装的女子，梳着高髻，戴着金凤步摇，立于宫殿廊下，神情端庄中带着一丝凌厉。

```
An elegant Chinese palace lady, regal and poised,
wearing ornate Han Dynasty court robes in deep red and gold,
elaborate hair ornaments with golden phoenix hairpins,
standing under palace eaves with red pillars behind,
dignified expression, sharp and intelligent eyes,
classical Chinese aesthetic, rich color palette,
semi-realistic, detailed embroidery and jewelry
```

**MJ 参数**：`--ar 2:3 --style raw --s 300`
**SD 参数**：同上

---

### 1.3 反派/配角

#### 阴鸷反派（男）

```
A sinister Chinese cultivator, gaunt and intense,
wearing black and dark purple robes with ominous patterns,
dark energy swirling around his hands, cold and calculating smirk,
standing in a shadowy cave, dim red lighting,
menacing atmosphere, sharp facial features, glowing red eyes,
dark fantasy art style, dramatic chiaroscuro
```

#### 魅惑反派（女）

```
A dangerously beautiful Chinese woman, seductive yet menacing,
wearing a tight black and red dress with serpent motifs,
dark red lips, eyes with a predatory gleam,
standing in a luxurious but ominous chamber,
low-key lighting, mysterious and deadly aura,
semi-realistic fantasy art, gothic undertones
```

#### 忠仆/导师型配角

```
An elderly Chinese sage, wise and serene,
white beard and long white hair tied in a simple bun,
wearing simple gray robes, holding a wooden staff,
sitting on a rock in a bamboo grove, soft morning light,
kind eyes, weathered face full of character,
Chinese ink wash painting influence, tranquil atmosphere
```

---

## 2. 场景图模板

### 2.1 战斗场景

**中文意图**：两位修仙者在空中激烈对战，各种法宝与法术光芒交织，天地变色。

```
Epic battle scene between two cultivators in mid-air,
swirling energy clashes of blue and red, flying swords and magical artifacts,
shockwaves rippling through clouds, mountains in the distance cracking,
lightning splitting the sky, dramatic color contrast,
cinematic wide angle, dynamic composition, motion blur on energy effects,
Chinese fantasy epic, breathtaking scale, high detail
```

**MJ 参数**：`--ar 16:9 --style raw --s 400 --chaos 10`
**SD 通用**：`Steps: 30, CFG: 8, Negative: static, boring, low energy`

---

### 2.2 城市/建筑

#### 现代都市

```
Breathtaking aerial view of a futuristic Chinese metropolis at night,
towering glass skyscrapers with neon lights, elevated maglev trains crossing between buildings,
holographic advertisements floating in the air, flying vehicles in organized lanes,
cyberpunk meets Chinese aesthetics, deep blue and purple color scheme,
wide angle, ultra-detailed, 8K, cinematic lighting
```

#### 古代宫殿

```
Magnificent Chinese imperial palace complex, Tang Dynasty architecture,
golden glazed roof tiles, red pillars and walls, white marble steps and railings,
surrounded by misty mountains, pink peach blossoms in foreground,
grandeur and majesty, symmetrical composition, warm golden hour light,
traditional Chinese painting style blended with 3D rendering, ultra-detailed
```

---

### 2.3 自然景观

#### 仙山云海

```
Breathtaking Chinese fantasy mountain landscape,
towering peaks piercing through sea of clouds,
floating islands with ancient temples and pine trees,
waterfalls cascading into the void, celestial deer drinking from a crystal stream,
golden sunrise illuminating the mist, ethereal atmosphere,
Chinese ink wash painting meets HD rendering, epic scale, 16:9
```

#### 秘境/洞天

```
Hidden mystical realm inside a mountain,
giant crystal formations glowing with internal light, bioluminescent mushrooms and plants,
underground lake reflecting crystalline ceiling, ancient ruins half-submerged,
ethereal blue-green lighting, mysterious atmosphere,
fantasy landscape, ultra-detailed environment art, 16:9
```

---

### 2.4 室内/日常

#### 书房/修炼室

```
Traditional Chinese study room, warm and scholarly atmosphere,
rosewood desk with brush, ink, paper and inkstone, scrolls on the wall,
incense burner with thin curling smoke, window overlooking bamboo garden,
soft candlelight and natural light filtering through paper windows,
cozy yet refined, rich wood tones, 3D render photorealistic
```

#### 现代公寓

```
Modern cozy apartment living room, warm afternoon sunlight through large windows,
minimalist Nordic style with Chinese decorative touches,
indoor plants, bookshelf filled with books, a cup of tea on the wooden coffee table,
soft cream and wood tones, relaxing atmosphere,
3D render, photorealistic, 8K, interior design style
```

---

## 3. 封面图模板

### 3.1 通用网文封面

**中文意图**：网文封面，上方留白给书名，中央是主角形象，背景营造小说氛围。

```
Novel cover design, vertical composition,
upper third blank space for title text,
center: {主角简要描述},
lower third: atmospheric elements ({氛围关键词}),
rich color palette matching novel theme,
commercial illustration style, clean composition,
leave negative space at top for text overlay
```

**MJ 参数**：`--ar 9:16 --style raw --s 300`
**重要**：生成后在中间上方留出足够的标题空间。

---

### 3.2 不同类型封面风格建议

| 类型 | 风格关键词 | 色调建议 | MJ 附加参数 |
|------|-----------|---------|------------|
| 玄幻 | Chinese fantasy epic, mystical | 金/蓝/紫 | `--s 400` |
| 仙侠 | ethereal, flowing, spiritual | 白/青/金 | `--s 300` |
| 都市 | modern, neon-lit, sleek | 蓝/紫/黑金 | `--s 200` |
| 古言 | classical, elegant, ink wash | 红/金/墨色 | `--s 250` |
| 悬疑 | noir, shadowy, dramatic contrast | 黑/红/灰 | `--c 20` |
| 甜宠 | soft, warm, romantic, gentle | 粉/奶油/浅蓝 | `--s 200` |
| 末世 | desolate, gritty, survival | 灰/橙/褪色 | `--c 30` |
| 科幻 | futuristic, holographic, sleek | 蓝/银/荧光绿 | `--s 250` |

---

## 4. 模型适配指南

### DALL-E 3

**特点**：
- 无需负向 prompt
- 对自然语言理解极佳，直接用中文描述效果就很好
- 自动输出 1024×1024（可追加 `wide` 或 `tall` 方向提示）
- 不适合超写实或 NSFW 内容

**推荐写法**：
```
高质量，{画风关键词}风格，{主体描述}，{背景氛围}。
构图：{构图提示}。光影：{光影描述}。
```

**示例 prompt**：
```
高质量，中国古风玄幻插画风格，
一位白衣剑客站在悬崖边，长发飘动，身后是云海和落日，
构图：竖版人物居中，仰视角度。光影：金色侧光打在人物身上。
```

---

### Midjourney

**特点**：
- 英文 prompt 为主，中文理解弱
- 需用 `--` 参数控制比例（`--ar`）、风格化（`--s`）、混乱度（`--c` 或 `--chaos`）
- 支持 `--no` 负向排除、`::权重` 关键词加权
- 擅长艺术风格，写实能力随版本提升

**关键词权重写法**（`::` 分隔，数字越大权重越高）：
```
Chinese cultivator::2 standing on mountain peak::1.5 misty atmosphere::1 --ar 2:3
```

**常用参数速查**：
| 参数 | 含义 | 常用值 |
|------|------|--------|
| `--ar` | 宽高比 | `2:3`(竖版) `16:9`(横版) `9:16`(手机封面) |
| `--s` | 风格化强度 | `100-1000`，`250` 为平衡起点 |
| `--c` | 变异度 | `0-100`，角色图用 `0-10`，创意场景用 `20-40` |
| `--style raw` | 减少艺术化处理 | 写实/摄影类推荐 |
| `--no` | 排除元素 | `--no text, watermark, signature` |

---

### Stable Diffusion (SD)

**特点**：
- 需完整的正负向 prompt
- 支持各类社区模型（Checkpoint/LoRA），风格控制极强
- 适合批量生成和精细调整

**推荐架构**：
```
{画质词} + {主体描述} + {风格词} + {光影/构图词}
```

**正向 prompt 模板**：
```
masterpiece, best quality, 8K, highly detailed,
{主体描述},
{画风词}, {光影氛围},
sharp focus, professional illustration
```

**负向 prompt 模板**（通用）：
```
lowres, bad anatomy, bad hands, text, error, missing fingers,
extra digit, fewer digits, cropped, worst quality, low quality,
normal quality, jpeg artifacts, signature, watermark, username,
blurry, deformed, ugly, mutation, disfigured, extra limbs,
fused fingers, long neck
```

**负向 prompt 追加**（角色图专用）：
```
multiple people, extra person, same face, clone
```

**推荐采样器**：`DPM++ 2M Karras` 或 `Euler a`
**推荐步数**：`25-35`
**推荐 CFG**：`7-9`

---

## 5. Prompt 写作原则

### 5.1 关键词密度与优先级

**公式**：主体 > 动作/姿态 > 服饰/装备 > 背景/环境 > 光影/氛围 > 画质/风格

- 把最重要的描述放在 prompt 最前面
- 每个要素用 1-2 个短语，避免冗余
- **好的 prompt**：`A swordsman in white robes, holding a glowing sword, standing in rain, dark forest background`
- **差的 prompt**：`There is a very handsome swordsman who is wearing beautiful white robes and he is holding a sword that is glowing very brightly...`

### 5.2 负面 prompt 建议

根据生成的常见问题，针对性加入：

| 问题 | 负向关键词 |
|------|-----------|
| 手部崩坏 | `bad hands, extra fingers, missing fingers, fused fingers` |
| 多人/克隆 | `multiple people, extra person, clone, duplicate` |
| 比例失调 | `bad anatomy, disfigured, deformed, long neck` |
| 画质低劣 | `lowres, blurry, jpeg artifacts, worst quality` |
| 多余元素 | `text, watermark, signature, logo, frame, border` |
| 面部丑陋 | `ugly, mutation, asymmetric face, crossed eyes` |

### 5.3 风格一致性保持

**核心：定好风格基调后不变。**

建议为每部小说定义**全局风格锚点**，放入小说配置文件或开篇设定中：

```yaml
# 风格锚点示例
style:
  base: "Chinese ink wash painting blended with semi-realistic 3D"
  color_palette: "墨色为主，金/朱红点缀"
  lighting: "柔和的自然光，偏暖色调"
  character_detail: "面部写实，服饰参考唐代壁画"
  environment_detail: "山水以写意为主，建筑以写实为主"
```

每次生成新图时，将风格锚点拼接到 prompt 末尾。

### 5.4 画面构图要点

| 构图类型 | 适用场景 | 描述方式 |
|---------|---------|---------|
| 中心构图 | 角色展示、封面 | `centered, symmetrical, front-facing portrait` |
| 三分法 | 角色+环境 | `subject on left third, landscape on right` |
| 对角构图 | 动态场景、战斗 | `diagonal composition, dynamic angle` |
| 仰视 | 展现威严/强大 | `low angle, looking up, heroic perspective` |
| 俯视 | 展现环境/渺小感 | `bird's eye view, overlooking` |
| 留白 | 封面、意境图 | `negative space, minimalist composition` |
| 特写 | 情感表达 | `close-up portrait, focused on face and expression` |
| 全景 | 大场景 | `wide shot, panoramic view` |

---

## 附录：快速搜索索引

| 需求 | 跳转 |
|------|------|
| 想给男主配图 | → 1.1 男性主角 |
| 想给女主配图 | → 1.2 女性主角 |
| 想给反派配图 | → 1.3 反派/配角 |
| 想画打斗场面 | → 2.1 战斗场景 |
| 想画城市背景 | → 2.2 城市/建筑 |
| 想画自然风光 | → 2.3 自然景观 |
| 想画室内场景 | → 2.4 室内/日常 |
| 想做封面 | → 3. 封面图模板 |
| 不知道模型特点 | → 4. 模型适配指南 |
| prompt 写不好 | → 5. Prompt 写作原则 |
