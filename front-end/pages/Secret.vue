<!-- 关于页 About -->
<script setup>
import '@/assets/icons/iconfont'

import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'
import { useMessage, NButton, NTooltip, NModal } from 'naive-ui'

import { checkLoginPromise } from '@/utils/userUtils';
import { getSecret, updateState, updateMessage } from '@/api/secretAPI'

const message = useMessage()
const router = useRouter()

// states
const secret_state = ref(-1); // -1: first see, 0: seen, 1: like, 2: dislike
let secret = null;
const msg_board_text = ref('');
const showMsgBoardModal = ref(false);

const typedLines = ref([]);
const typedIndex = ref(-1);
const if_finish_typed = ref(false);
const forbid = ref(false);

async function typeLines(words) {
  if_finish_typed.value = false;
  const lines = words.split('@');
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
    }, 100); // 每100毫秒打印一个字符
  });
}

function onReadyClicked() {
  if (secret) {
    secret_state.value = 0;
    updateState(secret_state.value).then(data => { })
    console.log(secret_state.value)
    typeLines(secret);
  } else message.error('糟糕,树洞门还没开，快找小小槟开门！');
}

function onLikeClicked() {
  secret_state.value = 1
  updateState(secret_state.value).then(data => {
    if (data && data.status === '0') { message.success("点赞成功！") }
  })
}

function onDislikeClicked() {
  secret_state.value = 2;
  updateState(secret_state.value).then(data => {
    if (data && data.status === '0') { message.success("反馈成功"); }
  })
}

function onMsgBoardClicked() {
  showMsgBoardModal.value = true;
}

function onUpdateMessage() {
  let update_message = msg_board_text.value
  update_message = update_message.replace(/\n/g, "@");
  updateMessage(update_message).then(data => {
    if (data && data.status === '0') {
      message.success("留言成功！");
      showMsgBoardModal.value = false;
    }
  });
}

onMounted(() => {
  checkLoginPromise().then((result) => {
    if (!result) {
      router.push('/')
      message.error("请先登录！")
    }

    const start_words_first =
      '欢迎来到秘密树洞！@' +
      '从今天到小小语毕业，这里每天都会浮现一条小小槟的“小秘密”。@' +
      '最后，这将变成你我共同的秘密。@' +
      '准备好接收第一条小秘密了吗？';
    const start_words = '准备好接收今天的小秘密了吗？';
    const greetings = [
      '不行哦，现在太晚啦，注意早点休息哦~',                   // 00:00-07:00
      '早安！新的一天，满载希望和活力，愿你拥有美妙的一天。',   // 07:00-11:00
      '中午好！记得给自己一个美味的午餐时间哦。',              // 11:00-13:00
      '下午好~希望你的午后充满阳光和效率。',                   // 13:00-17:00
      '晚上好！放松一下，享受属于你的美好夜晚。',              // 17:00-22:00
      '等你好久啦，看完早点休息哦~',                          // 22:00-24:00
    ];

    // update states
    getSecret().then(data => {
      if (data && data.status === '0') {
        data = data.data
        secret_state.value = parseInt(data.state)
        msg_board_text.value = data.message.replace(/@/g, "\n");
        secret = data.secret

        if (secret_state.value === -1) {
          // 得到格式化的当前日期
          const today = new Date();
          const year = today.getFullYear(); // 获取年份
          const month = today.getMonth() + 1; // 获取月份，月份是从0开始的，所以需要加1
          const date = today.getDate(); // 获取日期
          const hour = today.getHours(); // 获取小时
          let formattedDate = year + String(month).padStart(2, '0') + String(date).padStart(2, '0');
          // 根据日期判断提示词
          let type_words = start_words;
          if (formattedDate == '20240415') type_words = start_words_first;
          else if (parseInt(formattedDate) > 20240523) {
            type_words = "秘密树洞暂时关停啦~";
            forbid.value = true;
          } else if (hour >= 0 && hour < 7) {
            type_words = greetings[0];
            forbid.value = true;
          } else if (hour >= 7 && hour < 11) type_words = greetings[1] + '@' + start_words;
          else if (hour >= 11 && hour < 13) type_words = greetings[2] + '@' + start_words;
          else if (hour >= 13 && hour < 17) type_words = greetings[3] + '@' + start_words;
          else if (hour >= 17 && hour < 22) type_words = greetings[4] + '@' + start_words;
          else if (hour >= 22 && hour < 24) type_words = greetings[5] + '@' + start_words;
          typeLines(type_words);
        } else {
          typeLines(secret);
        }
      }
    });
  });
});
</script>

<template>
  <div class="container">
    <div class="typed-container">
      <p class="content" v-for="(line, index) in typedLines" :key="index" :class="{ 'blink': index == typedIndex }">{{
        line }}</p>
      <n-button size="large" type="info" round v-show="if_finish_typed & (secret_state == -1) & !forbid"
        @click="onReadyClicked"> 准备好了! </n-button>

      <div class="operate_bar" v-show="if_finish_typed & (secret_state != -1) & secret != null">
        <n-tooltip placement="bottom-end" trigger="hover">
          <template #trigger>
            <svg :class="['icon-btn', { 'light-icon': secret_state == 1 }]" @click="onLikeClicked">
              <use :xlink:href="'#icon-like'"></use>
            </svg>
          </template>
          如果喜欢今天的小秘密，请点个赞吧~
        </n-tooltip>

        <n-tooltip placement="bottom" trigger="hover">
          <template #trigger>
            <svg :class="['icon-btn', 'icon-r180', { 'light-icon': secret_state == 2 }]" @click="onDislikeClicked">
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
        <textarea type="text" name='name' id='name' maxlength="100" v-model='msg_board_text' placeholder="想说些什么呢~" />
        <span>{{ msg_board_text.length }}/100</span>
        <a @click="onUpdateMessage"> 确定 </a>
      </form>
    </div>
  </n-modal>
</template>

<style scoped>
.container {
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

.operate_bar {
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
  width: 24px;
  height: 24px;
  cursor: pointer;
}

.icon-btn:focus {
  outline: none;
}

.icon-btn:hover {
  fill: var(--color-light);
  filter: drop-shadow(0px 0px 2px var(--color-light));
}

.icon-r180 {
  transform: rotate(180deg);
}

@keyframes blink {
  50% {
    border-color: black;
  }
}

.msg-board {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 400px;
  padding: 20px;
  border-radius: 20px;
  color: var(--color-text);
  background-color: var(--color-background);
}

.msg-board textarea {
  resize: none;
  outline: none;
  border: 1px solid var(--color-text);
  width: 350px;
  height: 150px;
  transition: all 0.3s;
  font-size: 16px;
  color: var(--color-text);
  background-color: transparent;
}

.msg-board textarea:focus {
  border: 1px solid var(--color-light);
}

.msg-board span {
  display: block;
  text-align: center;
  color: var(--color-text-sub);
  margin-bottom: 5px
}

.msg-board a {
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
