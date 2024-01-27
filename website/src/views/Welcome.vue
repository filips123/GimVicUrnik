<script setup lang="ts">
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

import { EntityType } from '@/stores/settings'
import { useUserStore } from '@/stores/user'

import { updateAllData } from '@/composables/update'

import WelcomeInfo from '@/components/WelcomeInfo.vue'
import SettingsSelectEntity from '@/components/SettingsSelectEntity.vue'

const router = useRouter()

updateAllData()

const userStore = useUserStore()
userStore.$reset()
const { entityType } = storeToRefs(useUserStore())

const welcomeInfo = ref(true)
const settingsSelectEntity = ref(false)

watch(welcomeInfo, () => (settingsSelectEntity.value = true))
watch(entityType, () =>
  entityType.value === EntityType.None ? null : router.push({ name: 'timetable' }),
)
</script>

<template>
  <WelcomeInfo v-model="welcomeInfo" />
  <SettingsSelectEntity v-model="settingsSelectEntity" welcome />
</template>
