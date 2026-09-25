<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1); const out = ref(null)
const pasteOn = ref(false); const coverage = ref(5); const err = ref('')
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
  const s = await getJSON('/api/settings')
  if (s.paste_coverage_m2_per_l !== undefined) coverage.value = Number(s.paste_coverage_m2_per_l)
})
async function run(save) {
  err.value = ''; out.value = null
  const paste = pasteOn.value ? { paste_enabled: true, coverage: Number(coverage.value) } : { paste_enabled: false }
  try {
    if (save) {
      out.value = await postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, save: true, ...paste })
    } else {
      const q = new URLSearchParams({ wall_id: wallId.value, roll_id: rollId.value, ...paste })
      out.value = await getJSON(`/api/estimate?${q}`)
    }
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <label><input type="checkbox" v-model="pasteOn" /> 计入胶浆</label>
  <label v-if="pasteOn">涂布率（㎡/L）<input type="number" step="0.1" v-model.number="coverage" style="width:6rem" /></label>
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <p v-if="err" class="warn">{{ err }}</p>
  <div v-if="out" class="result-cols">
    <div class="col"><strong>{{ out.rolls }} 卷</strong> · {{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m</div>
    <div class="col" v-if="out.paste">净面积 {{ out.paste.net_area_m2 }}㎡ · 涂布率 {{ out.paste.coverage_m2_per_l }}㎡/L · <strong>胶浆 {{ out.paste.liters }}L</strong></div>
  </div>
  <DropStripBar v-if="out" :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" />
  </div>
</template>
