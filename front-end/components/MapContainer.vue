<template>
  <div id="amap">
    <div class="tool-container">
      <input
        id = "search_input"
        type="text"
        placeholder = "请输入搜索关键字"
        >
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";

let map = null;

onMounted(() => {
  window._AMapSecurityConfig = {
    securityJsCode: "467acecf4320cdce83d519705e1aad3b",
  };

  AMapLoader.load({
    key: "3fbe22db53162479e06074420635fba4", // 申请好的Web端开发者Key，首次调用 load 时必填
    version: "2.0",
    plugins: ['AMap.Scale', 'AMap.PlaceSearch', 'AMap.Autocomplete'],
  })
    .then((AMap) => {
      map = new AMap.Map("amap", {
        // 设置地图容器id
        viewMode: "3D", // 是否为3D地图模式
        zoom: 11, // 初始化地图级别
        center: [116.397428, 39.90923], // 初始化地图中心点位置
      });

      // 添加地图控件
      map.addControl(new AMap.Scale()); // 添加比例尺控件

      // 添加 AutoComplete, PlaceSearch 插件
      AMap.plugin(["AMap.AutoComplete", "AMap.PlaceSearch"], function () {
        const autoOptions = {
          input: "search_input", //使用联想输入的 input 的 id
        };
        const autocomplete = new AMap.AutoComplete(autoOptions);
        const placeSearch = new AMap.PlaceSearch({
          map: map,
        });
        autocomplete.on("select", function (e) {
          //针对选中的poi实现自己的功能
          placeSearch.search(e.poi.name);
        });
      });
    })
    .catch((e) => {
      console.log(e);
    });
});

onUnmounted(() => {
  map?.destroy();
});
</script>

<style scoped>
#amap {
  width: 100%;
  height: 100%;
}
.tool-container {
  position: absolute;
  top: 10px;
  left: 10px;
  height: 60px;
  width: 400px;
  z-index: 999;
}
</style>
