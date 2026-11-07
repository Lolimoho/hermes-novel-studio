"""Mock 适配器：不调用任何模型，按蓝图字段拼出结构完整的正文。

目的不是产出可读小说，而是让界面与数据流可验证：
有开头、有冲突、有章末钩子、字数接近目标，且每章不同。
"""

from __future__ import annotations

import random

from ..models import Chapter, ChapterPlan, Project

PLACES = ["旧城区的雨巷", "亮着灯的便利店门口", "半塌的剧院后台", "凌晨四点的天桥", "堆满纸箱的仓库"]
WEATHER = ["雨刚停", "风把塑料布吹得作响", "空气里有铁锈味", "路灯闪了两下", "远处传来末班车的声音"]
OPENERS = [
    "他到的时候，门已经开着。",
    "没有人告诉她该往哪走。",
    "事情是从一句多余的话开始的。",
    "那天的走廊比平时长。",
    "她把钥匙攥在手心，直到掌心发烫。",
]
BEATS = [
    "他没有立刻回答，只是把手里的东西放到桌上。",
    "对方看了她很久，像在确认一个早已知道的答案。",
    "话说到一半，外面传来脚步声，两个人都停了。",
    "她想过很多种可能，唯独没想过会是这样。",
    "空气里的那点余地，被这句话彻底用完了。",
]
CLOSERS = [
    "他忽然意识到，自己从一开始就问错了问题。",
    "门在身后合上，声音很轻，却像落下一道判决。",
    "手机在口袋里震动，屏幕上是一个不该出现的名字。",
    "她抬头，看见对面窗口的灯，灭了。",
    "那句没说完的话，最后变成了一声很轻的叹息。",
]
TITLE_WORDS = [
    "雨夜来客", "第一个名字", "旧账", "门后的声音", "空椅子", "不速之信",
    "第七天", "未寄出的信", "断线", "回声", "暗格", "旁听者",
    "错位", "余温", "静默的证词", "第二次见面", "陌生来电", "换季",
    "无人的站台", "纸上的名字", "旧照片", "夜航", "裂缝", "欠条",
]

OBJECTS = ["信封", "钥匙", "登记簿", "搪瓷杯", "旧照片", "手电", "雨伞", "纸条"]
GESTURES = [
    "把袖口往上卷了一截",
    "用指节敲了两下桌面",
    "把椅子往后挪了半寸",
    "低头看了看鞋尖上的水",
    "把灯罩转了个方向",
]
THOUGHTS = [
    "她想，这句话如果说出口，事情就没有回头路了",
    "他忽然明白，对方从头到尾都没有打算解释",
    "她知道自己应该拒绝，可拒绝的理由已经被昨天的自己用掉了",
    "他试着回忆更早的细节，脑子里却只剩下一段模糊的雨声",
]
LINES = [
    "「你来得比约定早。」",
    "「东西不在这里。」",
    "「我只问一次，你想清楚了再答。」",
    "「这不是你该管的事。」",
    "「你可以不信，但你已经看见了。」",
    "「明天这个时候，别再来了。」",
]



class MockAdapter:
    name = "mock"
    model = "mock-1"

    def _pick(self, seq: int, pool: list[str]) -> str:
        return pool[(seq - 1) % len(pool)]

    def generate_plans(
        self, project: Project, start_seq: int, count: int, words: int
    ) -> list[dict]:
        lead = "主角"
        plans: list[dict] = []
        for i in range(count):
            seq = start_seq + i
            title = TITLE_WORDS[(seq - 1) % len(TITLE_WORDS)]
            if seq > len(TITLE_WORDS):
                title = f"{title}（续）"
            plans.append(
                {
                    "title": f"{title}",
                    "goal": f"第 {seq} 章：{lead}要弄清上一章留下的线索，同时避开不该碰的人。",
                    "conflict": (
                        f"线索指向一个与 {project.genre or '故事'} 主线相反的方向；"
                        f"{lead}必须在今晚做出选择，而选择的代价会被下一章兑现。"
                    ),
                    "hook": CLOSERS[(seq - 1) % len(CLOSERS)],
                    "cast": "主角, 对手, 线人",
                    "words": words,
                }
            )
        return plans

    def generate_draft(
        self, project: Project, chapter: Chapter, plan: ChapterPlan | None, note: str
    ) -> str:
        seq = chapter.seq
        rnd = random.Random(f"{project.id}-{seq}")
        target = plan.words if plan and plan.words else project.words_per_chapter or 2000
        target = max(600, min(target, 6000))

        goal = plan.goal if plan and plan.goal else "把昨天的事弄明白"
        conflict = plan.conflict if plan and plan.conflict else "有人不希望他弄明白"
        hook = plan.hook if plan and plan.hook else rnd.choice(CLOSERS)
        cast = plan.cast if plan and plan.cast else "主角"
        place = rnd.choice(PLACES)
        weather = rnd.choice(WEATHER)

        paragraphs: list[str] = [f"{place}。{weather}。{rnd.choice(OPENERS)}"]
        if note:
            paragraphs.append(f"（作者要求：{note}）")
        paragraphs.append(
            f"这一章要解决的事很清楚：{goal}。{cast}里最先开口的是那个总在最后说话的人，"
            f"他把话讲得很慢，像在给谁留出反悔的时间。"
        )

        builders = [
            lambda: f"{rnd.choice(GESTURES)}。{rnd.choice(THOUGHTS)}。",
            lambda: f"{rnd.choice(LINES)}{rnd.choice(GESTURES)}，然后等着对方先开口。",
            lambda: (
                f"桌上摊着那只{rnd.choice(OBJECTS)}，边缘已经磨白。她没有立刻去拿，"
                f"先看了一遍窗外的街，确认没有第二个人跟进来。"
            ),
            lambda: f"{rnd.choice(BEATS)}{rnd.choice(BEATS)}",
            lambda: (
                f"他数了数口袋里的东西，又把{rnd.choice(OBJECTS)}放回去。"
                f"这件事如果现在不做，明天就再也找不到同样的机会。"
            ),
            lambda: (
                f"走廊尽头的灯忽明忽暗。{rnd.choice(THOUGHTS)}，"
                f"可她还是往前走了两步，脚步压在旧地板上，声音比预想的响。"
            ),
            lambda: (
                f"「{rnd.choice(['说下去', '然后呢', '你在怕什么'])}？」没人回答。"
                f"窗玻璃上有一层薄雾，手指划过去，痕迹很快又合上。"
            ),
            lambda: f"麻烦在于，{conflict}。这一点谁都没有挑明，但屋里所有人都听懂了。",
        ]

        guard = 0
        while sum(len(p) for p in paragraphs) < target * 0.92 and guard < 80:
            paragraphs.append(builders[guard % len(builders)]())
            guard += 1

        paragraphs.append(
            "外面的声音远了。桌上的东西还在原处，谁也没有先动。过了很久，"
            "有人伸手，把那张纸翻了过来——背面写着一行更小的字。"
        )
        paragraphs.append(hook)

        return "\n\n".join(paragraphs)

    def review(
        self, project: Project, chapter: Chapter, plan: ChapterPlan | None, content: str
    ) -> list[dict]:
        seq = chapter.seq
        length = len(content)
        target = plan.words if plan and plan.words else project.words_per_chapter or 2000
        findings: list[dict] = []

        if length < target * 0.5:
            findings.append(
                {
                    "round": 1,
                    "severity": "block",
                    "category": "structure",
                    "text": f"本章正文仅 {length} 字，未达到目标字数，冲突尚未展开就收尾。",
                }
            )
        else:
            findings.append(
                {
                    "round": 1,
                    "severity": "warn",
                    "category": "structure",
                    "text": "第三段的冲突推进略快，缺少一次试探，读者来不及建立预期。",
                }
            )

        if plan and plan.hook and plan.hook[:6] not in content:
            findings.append(
                {
                    "round": 1,
                    "severity": "warn",
                    "category": "structure",
                    "text": "章末未落到蓝图设定的钩子上，下一章的第一拍可能接不住。",
                }
            )

        findings.append(
            {
                "round": 2,
                "severity": "warn",
                "category": "fact",
                "text": f"第 {seq} 章提到的时间与上一章结尾相隔不明，建议补一个明确的时间锚点。",
            }
        )
        findings.append(
            {
                "round": 3,
                "severity": "hint",
                "category": "reading",
                "text": "同一段里连续出现两次「没有」，可换一处为动作描写，降低重复感。",
            }
        )
        findings.append(
            {
                "round": 4,
                "severity": "hint",
                "category": "rules",
                "text": "对照 rules.md：本章未出现句式红线，标点使用规范。",
            }
        )
        return findings
