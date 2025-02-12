<template>
  <div class="flex justify-center">
    <div class="space-y-4 max-w-4xl">
      <div v-for="(value, key) in state.dictionary" :key="key" class="ml-6">
        <div class="flex items-center space-x-2">
          <!-- Key Display -->
          <div class="font-medium mr-4">{{ convertFromSnakeCase(key) }}:</div>

          <!-- Object Type (Nested Dictionary) -->
          <div
            v-if="isObjectType(value)"
            @click="toggleCollapse(key)"
            class="cursor-pointer text-blue-500"
          >
            [{{ state.collapesdKeys.includes(key) ? "Expand" : "Collapse" }}]
          </div>

          <!-- Boolean Field -->
          <div v-if="typeof value === 'boolean'" class="flex items-center">
            <toggleSwitch v-model="state.dictionary[key]" />
          </div>

          <!-- Number Field (Integers and Decimals) -->
          <div v-else-if="typeof value === 'number'" class="flex-1 m-4">
            <InputNumber
              v-model.number="state.dictionary[key]"
              class="input-text"
              :step="value % 1 === 0 ? '1' : '0.01'"
            />
          </div>

          <!-- Handling list of objects -->
          <div
            v-else-if="Array.isArray(value) && isListOfObjects(value)"
            class="flex-1"
          >
            <div
              v-for="(value, key) in value"
              :key="`item-${key}`"
              class="border p-2 rounded my-2"
            >
              <SettingsRefactor
                v-if="!state.collapesdKeys.includes(key) && isObjectType(value)"
                :data="value"
                class="mt-2"
              />
            </div>
          </div>

          <!-- Fallback for other types -->
          <div v-else class="flex-1 m-4">
            <Textarea
              v-if="typeof value === 'string'"
              v-model="state.dictionary[key]"
            />
            <!-- Placeholder for other input types -->
          </div>

          <!-- Delete Button -->
          <Button @click="deleteKey(key)" label="Delete" class="ml-2 my-4" />
        </div>

        <!-- Recursive Component Call for nested dictionaries -->
        <SettingsRefactor
          v-if="!state.collapesdKeys.includes(key) && isObjectType(value)"
          :data="value"
          class="mt-2"
        />
      </div>

      <!-- UI to add a new key-value pair -->
      <div class="flex justify-center my-6">
        <InputText placeholder="New Key" v-model="newKey" class="mr-2" />
        <Textarea placeholder="New Value" v-model="newValue" />
        <Button @click="addKeyValue" label="Add" class="ml-2" />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, onMounted } from "vue"
  import { useUsers } from "@/store/modules/users"

  const userStore = useUsers()

  const props = defineProps({
    data: {
      type: Object,
      default: {}
    }
  })

  const convertFromSnakeCase = (k) => {
    k = k.replace(/_/g, " ")
    k = k.replace(/\w\S*/g, function (txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    })
    return k
  }

  // Methods
  const isObjectType = (value) =>
    value && typeof value === "object" && !Array.isArray(value)

  const toggleCollapse = (key) => {
    const index = state.collapesdKeys.indexOf(key)
    if (index > -1) {
      state.collapesdKeys.splice(index, 1)
    } else {
      state.collapesdKeys.push(key)
    }
  }

  const deleteKey = (key) => {
    Vue.delete(state.dictionary, key)
  }

  const addKeyValue = () => {
    if (state.newKey) {
      Vue.set(state.dictionary, state.newKey, state.newValue)
      state.newKey = ""
      state.newValue = ""
    }
  }

  const isListOfObjects = (list) =>
    list.every((item) => typeof item === "object" && !Array.isArray(item))

  const removeItemFromList = (key, index) => {
    state.dictionary[key].splice(index, 1)
  }

  const addItemToList = (key) => {
    // Adjust according to the structure of your objects
    state.dictionary[key].push({ name: "New Product", price: 0 })
  }

  const state = reactive({
    dictionary: null,
    newKey: null,
    newValue: null,
    collapesdKeys: []
  })

  onMounted(() => {
    state.dictionary = props.data
  })
</script>
