"""
WebMender AI — DOM Differ
Generates a human-readable and LLM-readable diff between two DOM snapshots.
"""

import difflib
import re
from typing import List


class DOMDiffer:
    """
    Lightweight DOM differ that:
    - Strips verbose attributes to focus on structural changes
    - Highlights added/removed elements, changed text content, and renamed labels
    - Returns a compact string diff suitable for LLM prompting
    """

    NOISE_ATTRS = re.compile(r'\s(data-v-[a-z0-9]+|class="[^"]{100,}")')

    def _clean(self, dom: str) -> str:
        """Remove noise attributes to focus on structural signal."""
        cleaned = self.NOISE_ATTRS.sub("", dom)
        # Collapse whitespace
        return "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())

    def diff(self, old_dom: str, new_dom: str, context_lines: int = 5) -> str:
        """
        Compute a unified diff between two DOM snapshots.
        Returns a compact diff string highlighting what changed.
        """
        old_lines = self._clean(old_dom).splitlines(keepends=True)
        new_lines = self._clean(new_dom).splitlines(keepends=True)

        diff_lines = list(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile="dom_before",
                tofile="dom_after",
                n=context_lines,
            )
        )

        if not diff_lines:
            return "No structural DOM change detected."

        # Extract high-signal lines (additions and removals)
        signal_lines = [
            line for line in diff_lines
            if line.startswith("+") or line.startswith("-")
        ]

        summary = f"Total changed lines: {len(signal_lines)}\n\n"
        summary += "".join(diff_lines[:150])  # cap at 150 lines for LLM context
        return summary

    def extract_interactive_elements(self, dom: str) -> List[dict]:
        """
        Parse clickable/interactive elements from a DOM snapshot.
        Returns a list of {tag, text, selector} dicts for the repair planner.
        """
        elements = []
        button_pattern = re.compile(
            r'<(button|a|input)[^>]*(?:id="([^"]*)")?[^>]*(?:class="([^"]*)")?[^>]*>(.*?)</',
            re.IGNORECASE | re.DOTALL,
        )
        for match in button_pattern.finditer(dom):
            tag, elem_id, elem_class, inner_text = match.groups()
            text = re.sub(r"<[^>]+>", "", inner_text or "").strip()[:80]
            if text or elem_id:
                elements.append({
                    "tag": tag,
                    "id": elem_id or "",
                    "class": (elem_class or "")[:60],
                    "text": text,
                    "selector": f"#{elem_id}" if elem_id else f"{tag}:contains('{text}')",
                })
        return elements[:30]  # return top 30 candidates
