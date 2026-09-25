<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const open = ref(null)
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
async function openRun(id) { open.value = await getJSON(`/api/runs/${id}`) }
</script>
<template>
  <div class="page"><h1>记录</h1>
  <ul><li v-for="r in items" :key="r.id">
    <a href="#" @click.prevent="openRun(r.id)">#{{ r.id }}</a>
    {{ r.wall_name }} → {{ r.result?.rolls }} 卷<template v-if="r.result?.paste"> · {{ r.result.paste.liters }} L 胶浆</template>
  </li></ul>
  <div v-if="open">
    <h2>run #{{ open.id }}</h2>
    <p>{{ open.wall_name }} / {{ open.roll_name }} · {{ open.created_at }}</p>
    <p>{{ open.result.rolls }} 卷 · {{ open.result.drops }} 条 · 每条 {{ open.result.drop_len_m }}m</p>
    <p v-if="open.result.paste">净面积 {{ open.result.paste.net_area_m2 }} ㎡ · 涂布率 {{ open.result.paste.coverage_m2_per_l }} ㎡/L · 胶浆 {{ open.result.paste.liters }} L</p>
    <p v-else>未计胶浆</p>
  </div>
  </div>
</template>
