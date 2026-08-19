<script setup lang="ts">
defineProps<{
  navigation: { title: string; link: string; icon: string }[]
  dimOthers?: boolean
  sportsActive?: boolean
}>()

const emit = defineEmits<{ sportsAdmin: [] }>()
let holdTimer: ReturnType<typeof setTimeout> | undefined
let holdTriggered = false

function startHold(link: string) {
  if (link !== 'sports') return
  holdTriggered = false
  holdTimer = setTimeout(() => {
    holdTriggered = true
    emit('sportsAdmin')
  }, 700)
}

function cancelHold() {
  if (holdTimer) clearTimeout(holdTimer)
  holdTimer = undefined
}

function handleClick(event: MouseEvent, link: string) {
  if (link === 'sports' && holdTriggered) {
    event.preventDefault()
    holdTriggered = false
  }
}
</script>

<template>
  <v-bottom-navigation
    grow
    role="navigation"
    aria-label="Navigacija"
    class="navigation-main d-print-none"
    :class="{ 'sports-navigation-active': dimOthers }"
  >
    <v-btn
      v-for="page in navigation"
      :key="page.link"
      :text="page.title"
      :aria-label="page.title"
      :prepend-icon="page.icon"
      :to="page.link === 'sports' && sportsActive ? { name: 'timetable' } : { name: page.link }"
      :class="{ 'navigation-dimmed': dimOthers && page.link !== 'sports' }"
      @pointerdown="startHold(page.link)"
      @pointerup="cancelHold"
      @pointerleave="cancelHold"
      @click="handleClick($event, page.link)"
      @contextmenu="page.link === 'sports' ? $event.preventDefault() : undefined"
    />
  </v-bottom-navigation>
</template>

<style scoped>
.navigation-main:not(.sports-navigation-active) :deep(.v-btn) {
  filter: none !important;
  opacity: 1 !important;
}

.navigation-dimmed {
  filter: saturate(0.25) brightness(0.7);
  opacity: 0.45;
  transition:
    filter 150ms ease,
    opacity 150ms ease;
}
</style>
