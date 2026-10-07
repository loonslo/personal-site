"use strict";

(() => {
  const root = document.documentElement;
  const seen = root.classList.contains("seen");

  // 滚动显现：只处理首屏以下的块，首屏内的块始终可见，不会先闪一下再淡入；
  // 本会话再次访问（boot.js 已加 seen）时全部直接可见。
  const items = document.querySelectorAll("[data-reveal]");
  if (!seen && items.length && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px" },
    );
    const fold = window.innerHeight * 0.92;
    items.forEach((element) => {
      // 视口高度为 0（后台预渲染、个别内置浏览器）时没法判断是否在首屏：不隐藏，宁可少一次动画也不让内容消失
      if (!fold || element.getBoundingClientRect().top < fold) return;
      element.classList.add("is-pending");
      observer.observe(element);
    });
  }

  // 意图预取：鼠标悬停约 65ms、手指按下或键盘聚焦到链接时，同源页面先预取，
  // 跨域的链接（各子站）先预连接；真正点下去时，Chrome/Edge 直接用这份缓存或已建好的连接。
  // 省流量模式、2G 和已处理过的地址跳过；失败不影响正常跳转。
  const connection = navigator.connection || {};
  if (connection.saveData || /(^|-)2g$/.test(connection.effectiveType || "")) return;

  const here = new URL(location.href);
  here.hash = "";
  const hinted = new Set([here.href]);
  let timer = 0;

  const hint = (rel, href) => {
    const link = document.createElement("link");
    link.rel = rel;
    link.href = href;
    document.head.append(link);
  };

  const warm = (anchor) => {
    const url = new URL(anchor.getAttribute("href"), location.href);
    if (!/^https?:$/.test(url.protocol)) return;
    if (url.origin !== location.origin) {
      if (!hinted.has(url.origin)) {
        hinted.add(url.origin);
        hint("preconnect", url.origin);
      }
      return;
    }
    url.hash = "";
    if (hinted.has(url.href) || anchor.hasAttribute("download") || anchor.getAttribute("target") === "_blank") return;
    hinted.add(url.href);
    hint("prefetch", url.href);
  };

  const anchorOf = (event) => (event.target instanceof Element ? event.target.closest("a[href]") : null);

  document.addEventListener(
    "mouseover",
    (event) => {
      const anchor = anchorOf(event);
      clearTimeout(timer);
      if (anchor) timer = setTimeout(() => warm(anchor), 65);
    },
    { passive: true },
  );
  document.addEventListener(
    "touchstart",
    (event) => {
      const anchor = anchorOf(event);
      if (anchor) warm(anchor);
    },
    { passive: true },
  );
  document.addEventListener("focusin", (event) => {
    const anchor = anchorOf(event);
    if (anchor) warm(anchor);
  });
})();
