<template>
  <div class="grid grid-cols-12 gap-4">
    <!-- <div class="col-span-6">
        <div class="card">
          <CreateCouponForm />
        </div>
      </div> -->
    <div class="col-span-12">
      <div class="card">
        <Toolbar class="mb-6">
          <template #start>
            <Button
              label="Add Coupon"
              icon="pi pi-plus"
              @click="state.createCouponForm = !state.createCouponForm"
              class="ml-4 p-button-success"
            />
          </template>
        </Toolbar>

        <CouponsList />
      </div>
    </div>
    <Dialog
      v-model:visible="state.createCouponForm"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="'Add Coupon'"
      :modal="true"
      class="p-fluid"
    >
      <CreateCouponForm
        @hide="state.createCouponForm = false"
      ></CreateCouponForm>
    </Dialog>
  </div>
</template>

<script setup>
  import CreateCouponForm from "./coupons/CreateCouponForm.vue"
  import CouponsList from "./coupons/CouponsList.vue"

  import { reactive, watch, onMounted } from "vue"
  import { useUsers } from "@/store/modules/users"

  const userStore = useUsers()

  const state = reactive({
    cms: null,
    loading: false,
    cmsId: null,
    createCouponForm: false
  })

  onMounted(async () => {
    console.log(userStore.cms)
    state.id = userStore.cms.id
    state.cms = userStore.cms
  })

  watch(
    () => userStore.cms,
    (newVal, oldVal) => {
      state.cms = newVal
    }
  )
</script>

<style></style>
