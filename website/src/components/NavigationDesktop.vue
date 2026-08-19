<script setup lang="ts">
import { mdiChevronLeft, mdiChevronRight } from '@mdi/js'
import { ref } from 'vue'

defineProps<{
  navigation: { title: string; link: string; icon: string }[]
}>()

const rail = ref(true)
const emit = defineEmits<{ sportsAdmin: [] }>()
let holdTimer: ReturnType<typeof setTimeout> | undefined

function startHold(link: string) {
  if (link !== 'sports') return
  holdTimer = setTimeout(() => emit('sportsAdmin'), 700)
}

function cancelHold() {
  if (holdTimer) clearTimeout(holdTimer)
  holdTimer = undefined
}
</script>

<template>
  <v-navigation-drawer :rail class="d-print-none">
    <v-list class="pt-0" tabindex="-2" aria-label="Navigacija">
      <v-list-item
        v-for="page in navigation"
        :key="page.link"
        :title="page.title"
        :aria-label="page.title"
        :prepend-icon="page.icon"
        :to="{ name: page.link }"
        tabindex="0"
        @pointerdown="startHold(page.link)"
        @pointerup="cancelHold"
        @pointerleave="cancelHold"
        @contextmenu="page.link === 'sports' ? $event.preventDefault() : undefined"
      />
    </v-list>
    <template #append>
      <v-list-item
        :aria-label="rail ? 'Strni' : 'Razširi'"
        :prepend-icon="rail ? mdiChevronRight : mdiChevronLeft"
        role="button"
        @click="rail = !rail"
      />
    </template>
  </v-navigation-drawer>
</template>
