<!-- 关于页 About -->
<script setup>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router'
  import { useMessage } from 'naive-ui'

  import { checkLogin } from '@/utils/userUtils';

  const message = useMessage()
  const router = useRouter()
  if(!checkLogin()) {
      router.push('/')
      message.error("请先登录！")
  }

  const typedText = ref("");
  const fullText = "你好，我是传信小鸽，负责这39天的小秘密传达~\n 这是第二行";
  const typingSpeed = 150;

  const typeWriterEffect = () => {
    let index = 0;
    const interval = setInterval(() => {
      typedText.value += fullText.charAt(index);
      index++;
      if (index > fullText.length) {
        clearInterval(interval);
      }
    }, typingSpeed);
  };

  onMounted(() => {
    typeWriterEffect();
  });
</script>

<template>
    <div class="container">
        <p class="content">{{ typedText }}</p>
        <p class="content1">{{ 123 }}</p>
    </div>
</template>

<style scoped>
    .container{
        height: calc(100vh - 80px);
        display: grid;
        place-items: center;
    }

    .content {
        font-size: 20px;
        height: 30px;
        padding-right: 2px;
        margin-bottom: 50px;
        border-right: 2px solid black;
        animation: blink 0.5s steps(1) infinite;
    }

    @keyframes blink { 50% { border-color: transparent;} }
</style>
