<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const openId = ref('')
const detail = ref(null)
const err = ref('')
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
async function openRun() {
  detail.value = null; err.value = ''
  if (!openId.value) return
  try { detail.value = await getJSON(`/api/runs/${openId.value}`) }
  catch (e) { err.value = `编号 ${openId.value} 不存在` }
}
</script>
<template>
  <div class="page"><h1>记录</h1>
  <p><label>按编号打开 <input v-model="openId" style="width:6rem" /></label>
  <button @click="openRun">打开</button> <span v-if="err" class="warn">{{ err }}</span></p>
  <div v-if="detail" class="roll-chip">
    #{{ detail.id }} {{ detail.wall_name }} → {{ detail.roll_name }}：
    {{ detail.result?.rolls }} 卷<template v-if="detail.result?.paste">
    · 净面积 {{ detail.result.paste.net_area_m2 }}㎡
    · 涂布率 {{ detail.result.paste.coverage_m2_per_l }}㎡/L
    · 胶浆 {{ detail.result.paste.liters }}L</template>
    · {{ detail.created_at }}
  </div>
  <ul><li v-for="r in items" :key="r.id">
    #{{ r.id }} {{ r.wall_name }} → {{ r.roll_name }}：{{ r.result?.rolls }} 卷<template v-if="r.result?.paste"> · 胶浆 {{ r.result.paste.liters }}L</template>
  </li></ul></div>
</template>
