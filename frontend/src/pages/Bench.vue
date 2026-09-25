<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1)
const pasteOn = ref(false); const out = ref(null); const err = ref('')
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
})
async function run(save) {
  err.value = ''; out.value = null
  try {
    out.value = save
      ? await postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, save: true, paste_enabled: pasteOn.value })
      : await getJSON(`/api/estimate?wall_id=${wallId.value}&roll_id=${rollId.value}&paste=${pasteOn.value ? 1 : 0}`)
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <label><input type="checkbox" v-model="pasteOn" /> 胶浆</label>
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <p v-if="err" class="warn">{{ err }}</p>
  <div v-if="out"><strong>{{ out.rolls }} 卷</strong> · {{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m
  <template v-if="out.paste"> · <strong>{{ out.paste.liters }} L 胶浆</strong> · 净面积 {{ out.paste.net_area_m2 }}㎡ · 涂布率 {{ out.paste.coverage_m2_per_l }}㎡/L</template>
  <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" /></div>
  </div>
</template>
