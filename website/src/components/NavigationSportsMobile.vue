<script setup lang="ts">
import { mdiBasketball, mdiCalendarWeek, mdiSoccer, mdiVolleyball } from '@mdi/js'

import type { SportSlug } from '@/stores/sports'

defineProps<{ section: SportSlug | 'schedule' }>()

const items: { title: string; value: SportSlug | 'schedule'; icon: string }[] = [
  { title: 'Razpored', value: 'schedule', icon: mdiCalendarWeek },
  { title: 'Nogomet', value: 'football', icon: mdiSoccer },
  { title: 'Odbojka', value: 'volleyball', icon: mdiVolleyball },
  { title: 'Košarka', value: 'basketball', icon: mdiBasketball },
]
</script>

<template>
  <nav role="navigation" aria-label="Vrsta tekem" class="sports-sub-navigation d-print-none">
    <v-btn
      v-for="item in items"
      :key="item.value"
      :value="item.value"
      :text="item.title"
      :aria-label="item.title"
      :prepend-icon="item.icon"
      :class="{ 'sports-sub-active': section === item.value }"
      stacked
      variant="text"
      :to="{ name: 'sports', params: { section: item.value } }"
    />
  </nav>
</template>

<style scoped>
.sports-sub-navigation {
  position: fixed;
  right: 0;
  bottom: 56px;
  left: 0;
  display: flex;
  height: 56px;
  margin: 0;
  background: rgb(var(--v-theme-surface));
  z-index: 1005;
}

.sports-sub-navigation :deep(.v-btn) {
  flex: 1 1 25%;
  height: 56px !important;
  border-radius: 0;
  font-size: 0.72rem;
  text-transform: none;
}

.sports-sub-active {
  background: rgba(var(--v-theme-on-surface), 0.14);
}
</style>
