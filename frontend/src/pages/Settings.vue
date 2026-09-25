<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const coverage = ref('')
const msg = ref('')
const err = ref('')
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  coverage.value = s.value.paste_coverage_m2_per_l ?? ''
})
async function save() {
  msg.value = ''; err.value = ''
  try {
    s.value = await putJSON('/api/settings', { paste_coverage_m2_per_l: String(coverage.value) })
    msg.value = '已保存'
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>设置</h1>
  <p><label>默认涂布率（㎡/L）<input v-model="coverage" style="width:6rem" /></label>
  <button @click="save">保存</button> <span>{{ msg }}</span></p>
  <p v-if="err" class="warn">{{ err }}</p>
  <pre>{{ s }}</pre></div>
</template>
