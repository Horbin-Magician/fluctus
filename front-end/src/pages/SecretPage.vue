<!-- 关于页 About -->
<!--
  TODO List：
    服务端：
      1、储存并返回小秘密
      2、记录用户的是否首次、点赞、踩、留言
    客户端
      1、点赞、踩点击功能
      2、留言面板
-->

<script setup>
  import '@/assets/icons/iconfont'

  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router'
  import { useMessage, NButton, NTooltip, NModal } from 'naive-ui'

  import { checkLogin } from '@/utils/userUtils';

  const message = useMessage()
  const router = useRouter()
  if(!checkLogin()) {
      router.push('/')
      message.error("请先登录！")
  }

  const secrets = [
    '今天是4月10日',
    '今天是4月11日',
    '今天是4月12日',
    '分手时想到什么。\n这最后的39天，让我和我的小秘密一同陪你走过~',
  ]

  const start_words = 
    '欢迎来到秘密树洞！\n' +
    '从今天到小小语毕业，这里每天都会浮现一条小小槟的“小秘密”。\n' +
    '最后，这将变成你我共同的秘密。\n' +
    '准备好接收第一条小秘密了吗？';
  
  const error_words = '糟糕,树洞门还没开，快找小小槟开门！';
  
  // states
  const if_ready = ref(false);
  const like_state = ref(0);
  const showMsgBoardModal = ref(false);
  
  const typedLines = ref([]);
  const typedIndex = ref(-1);
  const if_finish_typed = ref(false);
  const msg_board_text = ref('');

  async function typeLines(words) {
    const lines = words.split('\n');
    typedLines.value = [];
    for (const [index, line] of lines.entries()) {
      typedIndex.value = index;
      await typeLine(line);
      if (typedIndex.value < lines.length - 1) { typedLines.value.push(''); } // 为下一行准备
      await new Promise(resolve => setTimeout(resolve, 500));                 // 等待0.5秒后开始打印下一行
    }
    typedIndex.value = -1;
    if_finish_typed.value = true
  }

  function typeLine(line) {
    return new Promise(resolve => {
      let typedText = '';
      let index = 0;
      const intervalId = setInterval(() => {
        typedText += line[index];
        typedLines.value = [...typedLines.value.slice(0, -1), typedText];
        index++;
        if (index === line.length) {
          clearInterval(intervalId);
          resolve();
        }
      }, 10); // 每100毫秒打印一个字符 TODO 改回来
    });
  }

  function onReadyClicked(){
    if_ready.value = true; // TODO 保存记录到服务器，且刚开始时从服务器获取记录
    if_finish_typed.value = false;
    typeLines(secrets.pop()); secrets.pop()
  }

  // TODO
  function onLikeClicked(){
    like_state.value = 1
  }

  // TODO
  function onDislikeClicked(){
    like_state.value = 2
  }

  // TODO
  function onMsgBoardClicked(){
    showMsgBoardModal.value = true
  }

  onMounted(() => {
    typeLines(start_words); // TODO 判断是否为首次
  });
</script>

<template>
    <div class="container">
      <div class="typed-container">
        <p class="content" v-for="(line, index) in typedLines" :key="index" :class="{ 'blink': index==typedIndex }">{{ line }}</p>
        <n-button size="large" type="info" round v-show="if_finish_typed & !if_ready" @click="onReadyClicked"> 我准备好了! </n-button>
        
        <div class="operate_bar" v-show="if_finish_typed & if_ready">
          <n-tooltip placement="bottom-end" trigger="hover">
            <template #trigger>
              <svg :class="['icon-btn', {'light-icon': like_state==1}]" @click="onLikeClicked">
                <use :xlink:href="'#icon-like'"></use>
              </svg>
            </template>
            如果喜欢今天的小秘密，请点个赞吧~
          </n-tooltip>

          <n-tooltip placement="bottom" trigger="hover">
            <template #trigger>
              <svg :class="['icon-btn', 'icon-r180', {'light-icon': like_state==2}]" @click="onDislikeClicked">
                <use :xlink:href="'#icon-like'"></use>
              </svg>
            </template>
            如果不喜欢今天的小秘密，也请告知予我~
          </n-tooltip>

          <n-tooltip placement="bottom-start" trigger="hover">
            <template #trigger>
              <svg :class="['icon-btn']" @click="onMsgBoardClicked">
                <use :xlink:href="'#icon-msgboard'"></use>
              </svg>
            </template>
            有什么想说的也可以在这里留下哦~
          </n-tooltip>
        </div>
      </div>
    </div>
    <n-modal v-model:show="showMsgBoardModal" transform-origin="center">
        <div class="msg-board">
            <form @keyup.enter="onLogin">
                <textarea type="text" name='name' id='name' maxlength="100" v-model='msg_board_text' placeholder="想说些什么呢~"/>
                <span>{{msg_board_text.length}}/100</span>
                <a @click="onLogin"> 确定 </a>
            </form>
        </div>
    </n-modal>
</template>

<style scoped>
    .container{
        height: calc(100vh - 80px);
        display: grid;
        place-items: center;
    }

    .typed-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    .operate_bar{
      display: flex;
      justify-content: center;
      width: 100%;
      margin-top: 20px;
      gap: 30px;
    }

    .content {
        font-size: 18px;
        height: 30px;
        padding-right: 2px;
        margin-bottom: 10px;
        border-right: 2px solid transparent;
        line-height: 30px;
    }

    .blink {
        animation: blink 0.5s steps(1) infinite;
    }

    .light-icon {
      fill: var(--color-light);
    }

    .icon-btn {
      width: 28px;
      height: 28px;
      border-radius: 14px;
      cursor: pointer;
    }

    .icon-btn:focus {
        outline: none;
    }

    .icon-btn:hover{
      fill: var(--color-light);
      filter: drop-shadow( 0px 0px 2px var(--color-light) );
    }

    .icon-r180 {
      transform: rotate(180deg);
    }

    @keyframes blink { 50% { border-color: black;} }

    .msg-board{
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 400px;
      padding: 30px 30px 20px 30px;
      border-radius: 20px;
      color: var(--color-text);
      background-color: var(--color-background);
    }

    .msg-board textarea{
      resize: none;
      outline: none;
      border: 1px solid var(--color-text);
      width: 300px;
      height: 150px;
      transition: all 0.3s;
      font-size: 16px;
      color: var(--color-text);
      background-color: transparent;
    }

    .msg-board textarea:focus{
      border: 1px solid var(--color-light);
    }

    .msg-board span{
      display: block;
      text-align: center;
      color: var(--color-text-sub);
      margin-bottom: 5px
    }

    .msg-board a{
      display: block;
      text-align: center;
      color: var(--color-background);
      width: 100%;
      height: 40px;
      transition: all 0.3s;
      border-radius: 20px;
      background-color: var(--color-light);
      line-height: 40px;
    }
    .msg-board a:hover {
      cursor: pointer;
      box-shadow: 0 0 5px var(--color-light);
    }
</style>
