"""印章与月相图标。颜色全部由 CSS 变量控制，深浅色模式自动切换。"""

from __future__ import annotations

# 印章毛边滤镜，每页只定义一次，所有印章共用。
SVG_DEFS = (
    '<svg class="svg-defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>'
    '<filter id="seal-rough" x="-10%" y="-10%" width="120%" height="120%">'
    '<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="11" result="noise"/>'
    '<feDisplacementMap in="SourceGraphic" in2="noise" scale="2.2" xChannelSelector="R" yChannelSelector="G"/>'
    "</filter></defs></svg>"
)

# 月相：亮面由左向右增长。viewBox 14×14，圆心 (7,7)，半径 6。
_MOON_LIT = {
    "building": "",
    "intro": '<path d="M7 1a6 6 0 0 0 0 12z"/>',
    "open": '<path d="M7 1a6 6 0 0 0 0 12a3 6 0 0 0 0-12z"/>',
    "live": '<circle cx="7" cy="7" r="6"/>',
}


def seal(extra_class: str = "") -> str:
    """朱砂方印，中间留出纸色半月（白文印）。"""
    cls = f"seal {extra_class}".strip()
    return (
        f'<svg class="{cls}" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
        '<rect class="seal__bg" x="4" y="4" width="40" height="40" rx="4" filter="url(#seal-rough)"/>'
        '<circle class="seal__ring" cx="24" cy="24" r="10.5"/>'
        '<path class="seal__lit" d="M24 13.5a10.5 10.5 0 0 0 0 21z"/>'
        "</svg>"
    )


def moon(status: str, extra_class: str = "") -> str:
    """项目状态对应的月相，文字标签由调用方提供。"""
    lit = _MOON_LIT[status]
    cls = f"moon moon--{status} {extra_class}".strip()
    return (
        f'<svg class="{cls}" viewBox="0 0 14 14" aria-hidden="true" focusable="false">'
        '<circle cx="7" cy="7" r="6" fill="none" stroke="currentColor" stroke-width="1.2"/>'
        f'<g fill="currentColor">{lit}</g></svg>'
    )
