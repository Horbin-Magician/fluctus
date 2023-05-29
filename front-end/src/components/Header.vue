<!-- 页头 Header -->
<script setup>
    import { NModal, useMessage, NDrawer, NDrawerContent } from 'naive-ui'
    import { ref } from 'vue'
    import { RouterLink, useRouter, useRoute } from 'vue-router'

    import '@/assets/icons/iconfont'
    import { userlogin, initUser, checkLogin, userlogout } from '@/utils/userUtils';
    import storageUtils from '@/utils/storageUtils';
    
    const route = useRoute()
    const router = useRouter()
    const docBody = document.body
    const message = useMessage()

    const now_page =  ref(route.path.slice(1).split('/')[0])
    const showLoginModal = ref(false)
    const showLogoutModal = ref(false)
    const theme = ref(docBody.getAttribute('theme'))
    const user_name = ref('')
    const user_key = ref('')

    //初始化User信息
    initUser().then(data =>{
        if(data && data.status == 0) message.success(data.message)
    })
    const theme_storaged = storageUtils.getTheme()
    if(theme_storaged != null && theme_storaged != theme){
        docBody.setAttribute('theme', theme_storaged)
        theme.value = theme_storaged
    }

    router.afterEach((to, from) => {
        now_page.value = to.path.slice(1).split('/')[0]
    })

    const switchDocumentTheme = () => {
        theme.value = (theme.value == "light") ? "dark" : "light"
        docBody.setAttribute('theme', theme.value)
        storageUtils.setTheme(theme.value)
    }

    function onLogin(){
        userlogin(user_name.value, user_key.value).then(data => {
            if(data.status == '0') {
                showLoginModal.value = false
                message.success(data.message)
            }else{
                message.error(data.message)
            }
            
        })
    }
    function onLogoClicked(){
        if(checkLogin()){
            showLogoutModal.value = true
        }else showLoginModal.value = true
    }

    function logout(){
        userlogout()
        message.success("注销成功！")
    }
</script>

<template>
    <header>
        <div class="nav">
            <div class="logo">
                <svg class="icon" aria-hidden="true" @click="onLogoClicked">
                    <use xlink:href="#icon-logo"></use>
                </svg>
            </div>
            <!-- <router-link to="/calendar" :class="{active: now_page == 'calendar'}" class="link" v-if="checkLogin()"> 日历 </router-link> -->
        </div>
        <div class="nav">
            <router-link to="/" :class="{active: now_page == ''}" class="link"> 首页 </router-link>
            <!-- <router-link to="/repository" :class="{active: now_page == 'repository'}" class="link"> 仓库 </router-link> -->
            <router-link to="/about" :class="{active: now_page == 'about'}" class="link"> 关于 </router-link>
            <div class="theme" @click="switchDocumentTheme">
                <svg class="icon" aria-hidden="true">
                    <use xlink:href="#icon-sun" v-if="theme == 'light'"></use>
                    <use xlink:href="#icon-moon" v-if="theme == 'dark'"></use>
                </svg>
            </div>
        </div>
    </header>
    <n-modal v-model:show="showLoginModal" transform-origin="center">
        <div class="login">
            <form @keyup.enter="onLogin" autocomplete="off">
                <input type="text" name='name' id='name' v-model='user_name' placeholder="账号"/>
                <input type="password" name='pwd' id='pwd' v-model='user_key' placeholder="密码">
                <a @click="onLogin"> 登录 </a>
            </form>
        </div>
    </n-modal>
    <n-modal v-model:show="showLogoutModal" preset="dialog" :closable="false" type="warning"
         title="注销" content="是否注销当前登陆？" positive-text="确认" negative-text="取消" @positive-click="logout"/>
</template>

<style scoped>
header{
    height: 50px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
}
@keyframes shake{
    0%{
        transform: rotate(0);
    }
    50%{
        transform: rotate(-20deg);
    }
    100%{
        transform: rotate(0);
    }
}
.logo{
    height: 50px;
    margin-left: 20px;
    margin-right: 20px;
    transform-origin: center center;
}

.logo svg{
    width: 50px;
    height: 50px;
    color: var(--color-light);
}

.logo:hover{
    animation: shake 0.2s linear;
    cursor: pointer;
    filter: drop-shadow( 0px 0px 1px var(--color-light) );
}

.nav{
    display: flex;
    justify-content: center;
    height: 50px;
}

.nav .link{
    color: var(--color-text);
    display: block;
    margin-right: 20px;
    line-height: 50px;
    padding: 0px 10px;
    transition: all 0.2s ease;
    border-bottom: 2px solid transparent;
}
.nav .link:hover{
    color: var(--color-light);
    text-shadow: 0px 0px 1px var(--color-light);
    border-bottom: 2px solid var(--color-light);
}

.active{
    color: var(--color-light);
    border-bottom: 2px solid var(--color-light)!important;
}

.theme{
    width: 30px;
    height: 30px;
    margin-top: 10px;
    margin-right: 20px;
    transition: transform 0.2s ease;
    transform-origin: center center;
}
.theme:hover{
    cursor: pointer;
    transform: rotate(180deg);
    color: var(--color-light);
    filter: drop-shadow( 0px 0px 1px var(--color-light) );
}

.icon {
  width: 30px;
  height: 30px;
  overflow: hidden;
  fill: currentColor;
}

.logo-login svg{
    height: 60px;
    width: 60px;
    color: var(--color-light);
}

.login{
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 300px;
    padding: 30px 30px 20px 30px;
    border-radius: 20px;
    color: var(--color-text);
    background-color: var(--color-background);
}
.login input{
    outline: none;
    border: none;
    border-bottom: 1px solid var(--color-text);
    width: 100%;
    padding: 5px 0;
    margin-bottom: 20px;
    text-align: center;
    transition: all 0.3s;
    color: var(--color-text);
    background-color: transparent;
}
.login input:focus{
    border-bottom: 1px solid var(--color-light);
}
.login a{
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
.login a:hover {
    cursor: pointer;
    box-shadow: 0 0 5px var(--color-light);
}

/* 去掉input框中的小眼睛 */
#n1::-webkit-outer-spin-button,
#n1::-webkit-inner-spin-button{
    -webkit-appearance: none !important;
    margin: 0;
}
</style>