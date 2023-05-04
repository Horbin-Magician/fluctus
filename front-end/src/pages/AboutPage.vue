<!-- 关于页 About -->
<script setup>
    import '../assets/icons/iconfont'
</script>

<template>
    <div class="container">
        <div class="letter">
            <p>站名“云边小铺”，取自我挺喜欢的两本小说《云边有个小卖部》和《解忧杂货店》。</p>
            <p>想在云边拥有一个属于自己的港湾，这便是本站的起源了。</p>
            <p>想法有了，实施起来却很困难，正如你所见。不过没关系，我想这会是一个不错的开始。</p>
            <p>最后，欢迎光临~</p>
            <div class="date">
                <p>Horbin</p>
                <p>2021年05月22日</p>
            </div>
            <!-- <svg id="letter-logo" aria-hidden="true">
                <use xlink:href="#icon-homelogo"></use>
            </svg> -->
        </div>
    </div>
</template>

<style scoped>
    .container{
        height: calc(100vh - 80px);
        display: grid;
        place-items: center;
    }
    .letter{
        letter-spacing: 1px;
        line-height: 30px;
        padding: 30px 40px 40px 40px;
        border: 1px solid var(--color-light);
        box-shadow: 0 0 3px var(--color-light);
        margin-bottom: 100px;
    }
    .letter p{
        border-bottom: 1px solid var(--grey);
        padding: 0px 10px;
    }
    /* #letter-logo{
        fill: var(--grey);
        position: absolute;
        opacity: 0.2;
        right: 200px;
        bottom: 40px;
        width: 150px;
        height: 75px;
    } */
    .date{
        width: 100%;
        text-align: right;
    }
</style>
