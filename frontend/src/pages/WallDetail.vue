<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const props = defineProps({ id: String })
const wall = ref(null)
onMounted(async () => { wall.value = await getJSON(`/api/walls/${props.id}`) })
</script>
<template>
  <div class="page" v-if="wall"><h1>{{ wall.name }}</h1>
  <p v-if="wall.data_quality==='dirty'" class="warn">{{ wall.note }}</p>
  <p>周长 {{ wall.perimeter }} m，墙高 {{ wall.height }} m</p>
  <p>已登记门洞 {{ wall.door_area_m2 }} ㎡，净面积 {{ wall.net_area_m2 }} ㎡</p></div>
</template>
