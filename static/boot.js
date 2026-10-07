"use strict";

// 在 <head> 里同步执行，赶在首屏绘制之前给 <html> 定好状态：
// 入场动画只在本次会话首次访问时播放；站内再翻页由跨页过渡（styles.css 的 @view-transition）接手，
// 不再每页重放一遍“淡入”，看起来像又在加载。
// 隐私模式等读写 sessionStorage 失败时不加 seen，动画照常播放。
(() => {
  try {
    if (sessionStorage.getItem("hp:seen")) document.documentElement.classList.add("seen");
    else sessionStorage.setItem("hp:seen", "1");
  } catch (error) {
    // 始终播放
  }
})();
