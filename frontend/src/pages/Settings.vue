<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const coverage = ref('')
const msg = ref('')
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  coverage.value = s.value.paste_coverage ?? ''
})
async function saveCoverage() {
  msg.value = ''
  try {
    await putJSON('/api/settings/paste_coverage', { value: String(coverage.value) })
    s.value = await getJSON('/api/settings')
    msg.value = '已保存'
  } catch (e) { msg.value = e.message }
}
</script>
<template>
  <div class="page"><h1>设置</h1>
  <p>默认涂布率(㎡/L)<input v-model="coverage" type="number" min="0" step="0.1" />
  <button @click="saveCoverage">保存</button> {{ msg }}</p>
  <pre>{{ s }}</pre></div>
</template>
