<!-- 关于页 About -->
<script setup>
import '../assets/icons/iconfont'
</script>

<template>
  <div class="about-container">
    <div class="letter-card">
      <div class="letter-header">
        <div class="header-line"></div>
        <h1 class="site-title">起源</h1>
        <div class="header-line"></div>
      </div>
      
      <div class="letter-content">
        <p class="paragraph">
          站名"云边小铺"，取自我挺喜欢的两本小说《云边有个小卖部》和《解忧杂货店》。
        </p>
        <p class="paragraph">
          想在云边拥有一个属于自己的港湾，这便是本站的起源了。
        </p>
        <p class="paragraph">
          想法有了，实施起来却很困难，正如你所见。不过没关系，我想这会是一个不错的开始。
        </p>
        <p class="paragraph last-paragraph">
          最后，欢迎光临~
        </p>
      </div>
      
      <div class="letter-footer">
        <div class="signature">
          <p class="author">Horbin</p>
          <p class="date">2021年05月22日</p>
        </div>
      </div>
      
      <div class="corner-decoration top-left"></div>
      <div class="corner-decoration top-right"></div>
      <div class="corner-decoration bottom-left"></div>
      <div class="corner-decoration bottom-right"></div>
    </div>
  </div>
</template>

<style scoped>
.about-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  font-family: 'Lucida Handwriting', 'Apple Chancery', cursive;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

/* 信件卡片 */
.letter-card {
  position: relative;
  max-width: 900px;
  width: 100%;
  background: var(--color-background);
  border: 2px solid var(--color-light);
  border-radius: 16px;
  padding: 30px 40px;
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.1),
    0 0 20px var(--color-light-light);
  animation: slideIn 0.8s ease-out;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  z-index: 1;
}

.letter-card:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 15px 50px rgba(0, 0, 0, 0.15),
    0 0 30px var(--color-light-light);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卡片头部 */
.letter-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 25px;
}

.header-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(
    to right,
    transparent,
    var(--color-light),
    transparent
  );
  animation: lineExpand 1s ease-out 0.3s backwards;
}

@keyframes lineExpand {
  from {
    transform: scaleX(0);
  }
  to {
    transform: scaleX(1);
  }
}

.site-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-light);
  letter-spacing: 3px;
  margin: 0;
  animation: titleFade 0.8s ease-out 0.5s backwards;
}

@keyframes titleFade {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 信件内容 */
.letter-content {
  margin-bottom: 25px;
}

.paragraph {
  color: var(--color-text);
  font-size: 20px;
  line-height: 1.8;
  letter-spacing: 0.5px;
  padding: 8px 0;
  margin: 0;
  position: relative;
  animation: fadeInUp 0.6s ease-out backwards;
}

.paragraph:not(.last-paragraph)::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    var(--color-text-sub-sub),
    transparent
  );
  opacity: 0.3;
}

.paragraph:nth-child(1) {
  animation-delay: 0.6s;
}

.paragraph:nth-child(2) {
  animation-delay: 0.7s;
}

.paragraph:nth-child(3) {
  animation-delay: 0.8s;
}

.paragraph:nth-child(4) {
  animation-delay: 0.9s;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.last-paragraph {
  font-weight: 500;
  color: var(--color-light);
}

/* 信件尾部 */
.letter-footer {
  display: flex;
  justify-content: flex-end;
  animation: fadeInUp 0.6s ease-out 1s backwards;
}

.signature {
  text-align: right;
}

.author {
  font-size: 20px;
  font-weight: 400;
  color: var(--color-light);
  margin: 0 0 5px 0;
  letter-spacing: 2px;
  font-style: italic;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.date {
  font-size: 13px;
  color: var(--color-text-sub);
  margin: 0;
  letter-spacing: 0.5px;
}

/* 角落装饰 */
.corner-decoration {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-light);
  opacity: 0.6;
  animation: cornerGlow 2s ease-in-out infinite;
}

.top-left {
  top: 15px;
  left: 15px;
  border-right: none;
  border-bottom: none;
  border-top-left-radius: 6px;
}

.top-right {
  top: 15px;
  right: 15px;
  border-left: none;
  border-bottom: none;
  border-top-right-radius: 6px;
  animation-delay: 0.5s;
}

.bottom-left {
  bottom: 15px;
  left: 15px;
  border-right: none;
  border-top: none;
  border-bottom-left-radius: 6px;
  animation-delay: 1s;
}

.bottom-right {
  bottom: 15px;
  right: 15px;
  border-left: none;
  border-top: none;
  border-bottom-right-radius: 6px;
  animation-delay: 1.5s;
}

@keyframes cornerGlow {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .letter-card {
    padding: 25px 30px;
  }
  
  .site-title {
    font-size: 22px;
    letter-spacing: 2px;
  }
  
  .paragraph {
    font-size: 14px;
    line-height: 1.7;
    padding: 6px 0;
  }
  
  .letter-header {
    margin-bottom: 20px;
  }
  
  .letter-content {
    margin-bottom: 20px;
  }
}

@media (max-width: 480px) {
  .letter-card {
    padding: 20px 25px;
  }
  
  .site-title {
    font-size: 20px;
    letter-spacing: 2px;
  }
  
  .paragraph {
    font-size: 14px;
    padding: 5px 0;
  }
  
  .header-line {
    display: none;
  }
  
  .letter-header {
    margin-bottom: 18px;
  }
  
  .letter-content {
    margin-bottom: 18px;
  }
}
</style>
