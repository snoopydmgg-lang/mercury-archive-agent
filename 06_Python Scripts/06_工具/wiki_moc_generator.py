"""
Wiki 横向链接生成器
功能：计算笔记相似度，>= 0.65 时在双方笔记底部互相写入关联链接
"""

import re
import sys
import io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WIKI_ROOT = Path("E:/1.work/douyin/1.shuixing/Wiki知识库/wiki")
MIN_SIMILARITY = 0.65


class Note:
    def __init__(self, path: Path):
        self.path = path
        self.title = ""
        self.topics = []
        self.related_notes = []
        self.core_points = []
        self.category = ""
        self.concepts = []
        self.relative_path = ""
        self._parse()

    def _parse(self):
        try:
            content = self.path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = self.path.read_text(encoding="gbk", errors="ignore")

        self.relative_path = str(self.path.relative_to(WIKI_ROOT))

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_text = parts[1]
                self.title = self._get_field(fm_text, "title")
                self.topics = self._get_list(fm_text, "适用选题方向")
                self.related_notes = self._get_related(fm_text)
                self.core_points = self._get_list(fm_text, "核心观点")
                self.category = self.path.parent.name

        self._extract_concepts()

    def _get_field(self, text: str, key: str) -> str:
        for p in [rf'^{key}:\s*(.+?)(?=\n[A-Za-z\-]|$)', rf'^{key}:\s*"(.+?)"']:
            m = re.search(p, text, re.MULTILINE | re.DOTALL)
            if m:
                return m.group(1).strip()
        return ""

    def _get_list(self, text: str, key: str) -> list:
        m = re.search(rf'^{key}:\s*\n((?:\s*[-*]\s*.+\n)*)', text, re.MULTILINE)
        if m:
            return re.findall(r'^\s*[-*]\s*(.+)', m.group(1), re.MULTILINE)
        return []

    def _get_related(self, text: str) -> list:
        related_text = self._get_field(text, "关联笔记")
        if not related_text:
            return []
        matches = re.findall(r'\[\[wiki/([^\]]+)\]\]', related_text)
        return [m.replace("/", "_") for m in matches]

    def _extract_concepts(self):
        text_parts = [self.title] + self.topics
        for p in self.core_points:
            if isinstance(p, str):
                text_parts.append(p)

        text = " ".join(text_parts)
        words = re.findall(r'[\u4e00-\u9fa5]{2,5}', text)
        stopwords = {
            "的", "了", "和", "与", "或", "在", "是", "为", "有", "之", "以", "及", "等", "一个",
            "如何", "怎么", "什么", "为什么", "我们", "他们", "可以", "能够", "通过", "进行",
            "实现", "作为", "对于", "关于", "但是", "以及", "此外", "同时", "因此", "所以",
            "因为", "虽然", "如果", "当", "时", "来源", "核心观点", "适用选题方向",
            "关联笔记", "录入日期", "标题", "待整理"
        }
        filtered = [w for w in words if w not in stopwords and len(w) >= 2]
        freq = defaultdict(int)
        for w in filtered:
            freq[w] += 1
        self.concepts = [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:6]]


class KnowledgeGraph:
    def __init__(self):
        self.notes: dict[str, Note] = {}
        self.edges: dict[tuple[str, str], float] = {}

    def add_note(self, note: Note):
        self.notes[note.path.stem] = note

    def build_edges(self):
        note_keys = list(self.notes.keys())
        raw_edges = []

        for i, k1 in enumerate(note_keys):
            for k2 in note_keys[i+1:]:
                w = self._calc(k1, k2)
                if w > 0:
                    raw_edges.append((k1, k2, w))

        node_edges = defaultdict(list)
        for k1, k2, w in raw_edges:
            node_edges[k1].append((k2, w))
            node_edges[k2].append((k1, w))

        for node, edges in node_edges.items():
            edges.sort(key=lambda x: x[1], reverse=True)
            for neighbor, weight in edges[:5]:
                if weight >= MIN_SIMILARITY:
                    self.edges[(node, neighbor)] = weight
                    self.edges[(neighbor, node)] = weight

    def write_lateral_links(self):
        written = 0
        existing_links: dict[str, set[str]] = defaultdict(set)

        for (k1, k2), weight in list(self.edges.items()):
            if weight < MIN_SIMILARITY:
                continue
            if k2 in existing_links[k1]:
                continue

            for note_key, neighbor_key in [(k1, k2), (k2, k1)]:
                note = self.notes[note_key]
                neighbor = self.notes[neighbor_key]

                try:
                    content = note.path.read_text(encoding="utf-8")
                except:
                    content = note.path.read_text(encoding="gbk", errors="ignore")

                neighbor_rel = neighbor.relative_path.replace("\\", "/")
                if neighbor_rel in content:
                    continue

                if content.startswith("---"):
                    parts = content.split("---", 2)
                    body = parts[2] if len(parts) >= 3 else ""
                    new_body = body.rstrip() + f"\n\n关联：[[wiki/{neighbor_rel}]]（相似度: {weight:.2f}）\n"
                    new_content = content[:len(content) - len(body)] + new_body
                else:
                    new_content = content.rstrip() + f"\n\n关联：[[wiki/{neighbor_rel}]]（相似度: {weight:.2f}）\n"

                note.path.write_text(new_content, encoding="utf-8")
                written += 1

            existing_links[k1].add(k2)
            existing_links[k2].add(k1)

        return written

    def _jaccard(self, s1: set, s2: set) -> float:
        if not s1 or not s2:
            return 0.0
        return len(s1 & s2) / len(s1 | s2)

    def _calc(self, k1: str, k2: str) -> float:
        n1, n2 = self.notes[k1], self.notes[k2]

        explicit = k2 in n1.related_notes or k1 in n2.related_notes
        topics1 = set(t for t in n1.topics if t and t != "(待整理)")
        topics2 = set(t for t in n2.topics if t and t != "(待整理)")
        topic_sim = self._jaccard(topics1, topics2)
        concept_sim = self._jaccard(set(n1.concepts), set(n2.concepts))
        same_cat = 1 if n1.category == n2.category else 0

        raw = (3.0 if explicit else 0.0) + topic_sim * 2.0 + concept_sim * 1.0 + same_cat * 0.1
        return min(raw / 3.0, 1.0)


def main():
    print("[Scan]...")
    md_files = []
    for ext in ["*.md", "*.MD"]:
        md_files.extend(WIKI_ROOT.rglob(ext))

    print(f"   {len(md_files)} files")

    graph = KnowledgeGraph()
    for f in md_files:
        if f.name in ["MOC.md", "index.md"]:
            continue
        note = Note(f)
        if note.title:
            graph.add_note(note)

    print(f"   {len(graph.notes)} notes parsed")

    print("[Build] graph...")
    graph.build_edges()
    strong = sum(1 for w in graph.edges.values() if w >= MIN_SIMILARITY)
    print(f"   {len(graph.edges)//2} edges, {strong} strong")

    print("[Write] lateral links...")
    links_written = graph.write_lateral_links()
    print(f"   {links_written} links written")
    print("[Done]")


if __name__ == "__main__":
    main()
