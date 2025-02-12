<template>
  <div>
    <div>
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div v-if="isAdmin" class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >First Name <span style="color: red">*</span></label
          >
          <InputText
            placeholder="First Name"
            v-model="state.userCommission.user.first_name"
            :class="{ 'p-invalid': v$.userCommission.user.first_name.$invalid }"
            id="cost"
            class="'p-component p-inputtext-fluid'"
            type="text"
          />
        </div>
        <div v-if="isAdmin" class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Last Name <span style="color: red">*</span></label
          >
          <InputText
            placeholder="Last Name"
            v-model="state.userCommission.user.last_name"
            :class="{ 'p-invalid': v$.userCommission.user.last_name.$invalid }"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
        <div v-if="isAdmin" class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Display Name</label
          >
          <InputText
            placeholder="Display Name"
            v-model="state.userCommission.user.display_name"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>

        <div v-if="isAdmin" class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Email</label
          >
          <InputText
            placeholder="Email"
            v-model="state.userCommission.user.email"
            :class="{ 'p-invalid': v$.userCommission.user.email.$invalid }"
            class="p-component p-inputtext-fluid"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field" :class="!isAdmin ? '' : 'md:col-3'">
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Phone</label
          >
          <InputMask
            id="phone"
            v-model="state.userCommission.user.phone"
            class="p-component p-inputtext-fluid"
            mask="(999)-999-9999"
            placeholder="999-99-9999"
          />
        </div>
        <div
          v-if="!isAdmin"
          class="col-span-12 mb-4 field"
          :class="!isAdmin ? '' : 'md:col-3'"
        >
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Display Name (appears on customer invoices)</label
          >
          <InputText
            placeholder="Display Name"
            v-model="state.userCommission.user.display_name"
            id="cost"
            class="p-component p-inputtext-fluid"
            type="text"
          />
        </div>
        <div v-if="isAdmin" class="col-span-12 mb-4 field md:col-span-3">
          <label for="role" class="font-medium text-900 dark:text-0"
            >Role<span style="color: red">*</span></label
          >
          <Select
            placeholder="Select role"
            :options="state.roles"
            v-model="state.userCommission.user.role_id"
            class="p-component p-inputtext-fluid"
            id="role"
            type="text"
            optionLabel="label"
            optionValue="value"
            @change="selectedRoleLabel"
          />
        </div>
        <div
          v-if="
            !state.is_percentage && $ability.can('update', 'user-commission')
          "
          class="col-span-12 mb-4 field md:col-span-3"
        >
          <label for="flatCommission" class="font-medium text-900 dark:text-0"
            >Flat Commission Rate</label
          >
          <InputText
            placeholder="Flat Commission Rate"
            v-model="state.userCommission.commission.flat_commission"
            class="p-component p-inputtext-fluid"
            id="flatCommission"
            type="number"
          />
        </div>
        <div
          v-if="
            state.is_percentage && $ability.can('update', 'user-commission')
          "
          class="col-span-12 mb-4 field md:col-span-3"
        >
          <label
            for="percentageCommission"
            class="font-medium text-900 dark:text-0"
            >Percentage Commission Rate</label
          >
          <InputText
            placeholder="Percentage Commission Rate"
            v-model="state.userCommission.commission.commission_percentage"
            class="p-component p-inputtext-fluid"
            id="percentageCommission"
            type="number"
          />
        </div>
        <div
          v-if="$ability.can('update', 'user-commission')"
          class="col-span-12 mb-4 field md:col-span-3"
        >
          <label for="effectiveDate" class="font-medium text-900 dark:text-0"
            >Effective Commission Change Date</label
          >
          <DatePicker
            inputId="basic"
            dateFormat="m/d/y"
            placeholder="Set Date"
            class="p-component p-inputtext-fluid"
            v-model="state.userCommission.commission.commission_effective_date"
          />
        </div>

        <div
          v-if="$ability.can('update', 'user-commission')"
          class="col-span-12 mb-4 field md:col-span-3"
        >
          <label class="font-medium text-900 dark:text-0"
            >Rental Total Flat Commission Rate</label
          >
          <InputText
            placeholder="Rental Total Flat Commission Rate"
            class="p-component p-inputtext-fluid"
            v-model="
              state.userCommission.commission.rental_total_flat_commission_rate
            "
            type="number"
          />
        </div>

        <div
          v-if="$ability.can('update', 'user-commission')"
          class="col-span-12 mb-4 field md:col-span-2"
        >
          <label for="percentage" class="block font-medium text-900 dark:text-0"
            >Is Percentage</label
          >
          <toggleSwitch
            v-model="state.is_percentage"
            id="percentage"
            @change="changingCommissionType"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-2">
          <label for="active" class="block font-medium text-900 dark:text-0"
            >Birthday</label
          >
          <DatePicker
            v-model="state.userCommission.user.birthday"
            dateFormat="yy-mm-dd"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-2">
          <label for="active" class="block font-medium text-900 dark:text-0"
            >Shirt size</label
          >
          <Dropdown
            v-model="state.userCommission.user.shirt_size"
            :options="state.shirts"
            optionLabel="name"
            optionValue="value"
            placeholder="Select a shirt size"
            class="w-full md:w-14rem"
          />
        </div>
        <div
          class="col-span-12 mb-4 field md:col-span-2"
          v-if="state.is_sales_agent"
        >
          <label for="active" class="block font-medium text-900 dark:text-0"
            >Team leader</label
          >
          <Dropdown
            v-model="state.userCommission.user.team_leader_id"
            :options="state.team_leads"
            optionLabel="label"
            optionValue="value"
            placeholder="Select manager/director"
            class="w-full md:w-14rem"
          />
        </div>
        <div class="col-span-12 mb-4 field">
          <label for="active" class="block font-medium text-900 dark:text-0"
            >Mailing Address</label
          >
          <InputText
            placeholder="Mailing Address"
            class="p-component p-inputtext-fluid"
            v-model="state.userCommission.user.mailing_address"
            type="text"
          />
        </div>
        <div
          v-if="$isObjectPopulated(userProp) && isAdmin"
          class="col-span-12 mb-4 field md:col-span-2"
        >
          <label for="active" class="block font-medium text-900 dark:text-0"
            >Is Active</label
          >
          <toggleSwitch
            :disabled="!$ability.can('update', 'user-suspend')"
            v-model="state.userCommission.user.is_active"
          />
        </div>
      </div>
    </div>
    <Button
      :label="$isObjectPopulated(userProp) ? 'Update User' : 'Create User'"
      @click="createUpdateUser"
      :loading="state.loading"
      icon="pi pi-user"
      class="w-auto"
    ></Button>
  </div>
</template>

<script setup>
  import {
    reactive,
    computed,
    onMounted,
    inject,
    defineEmits,
    provide,
    watch
  } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
  import cloneDeep from "lodash.clonedeep"

  import UsersService from "@/service/User"
  import UserApi from "@/api/user"
  import InventoryService from "@/service/Inventory"

  import { useToast } from "primevue/usetoast"
  import { useUsers } from "@/store/modules/users"
  import { ABILITY_TOKEN } from "@casl/vue"
  import DateRangeSelection from "../rankings/DateRangeSelection.vue"
  import { useUrlSearchParams } from "@vueuse/core"
  import Dropdown from "primevue/dropdown"

  const $ability = inject(ABILITY_TOKEN)
  provide("$ability", $ability)

  const toast = useToast()

  const userService = new UsersService()
  const userApi = new UserApi()
  const userStore = useUsers()
  const inventoryService = new InventoryService()

  const stateService = new StateService()

  const { userProp, isAdmin } = defineProps({
    userProp: {
      type: Object,
      default: () => ({})
    },
    isAdmin: {
      type: Boolean,
      default: true
    }
  })

  const search = (event) => {
    state.team_leads = state.team_leads
  }

  const emit = defineEmits(["hide"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const isCreate = computed(() => {
    return !$isObjectPopulated(userProp)
  })

  const swapOldUser = (updatedUser) => {
    const index = cloneDeep(userStore.users)
      .map((u) => u.id)
      .indexOf(updatedUser.id)
    let clonedUsers = cloneDeep(userStore.users)
    clonedUsers[index] = userService.dtoUser(updatedUser)
    userStore.setUsers(clonedUsers.map((u) => userService.dtoUser(u)))
  }

  onMounted(async () => {
    state.statesList = stateService.getStates()
    state.roles = userStore.roles
      .filter((r) => r.name.toLowerCase() !== "superadmin") // Exclude "superadmin"
      .map((r) => ({ label: r.name, value: r.id }))
    resetUser()
    if (
      state.userCommission.commission.commission_percentage !== 0 &&
      state.userCommission.commission.commission_percentage !== null
    ) {
      state.is_percentage = true
    } else {
      // if the commission percentage is 0 then that means there is a flat commission
      if (
        state.userCommission.commission.flat_commission == 0 ||
        state.userCommission.commission.flat_commission == null
      ) {
        state.is_percentage = true
      } else {
        // unless there is not and then that means that this user does not have any commission history
        state.is_percentage = false
      }
    }
    selectedRoleLabel()
    if (!userProp && state.selected_role_label !== "sales_agent") {
      changingCommissionType()
      state.is_percentage = true
    }
    const { data, error } = await userApi.getRoles()
    state.roles_rates = data.value

    const team_leads_roles = userStore.roles.filter(
      (r) =>
        r.name.toLowerCase() == "sales_manager" ||
        r.name.toLowerCase() == "sales_director"
    )

    const users = await userApi.getUsers()
    state.sales_managers_and_directors = []
    users.data.value.forEach((u) => {
      for (var i = 0; i < team_leads_roles.length; i++) {
        if (u.role_id == team_leads_roles[i].id && u.is_active == true) {
          state.sales_managers_and_directors.push(u)
        }
      }
    })
    state.team_leads = state.sales_managers_and_directors.map((el) => {
      return {
        label: el.full_name,
        value: el.id
      }
    })

    const sales_agent_role = userStore.roles.filter(
      (r) => r.name.toLowerCase() == "sales_agent"
    )
    state.is_sales_agent =
      state.userCommission.user.role_id == sales_agent_role[0].id
  })

  const selectedRoleLabel = () => {
    let selectedRoleId = state.userCommission.user.role_id
    let selectedRole = state.roles.find((role) => role.value === selectedRoleId)
    state.selected_role_label = selectedRole ? selectedRole.label : ""
  }

  // this will be used to wipe the commission types every time they toggle the is percentage button so that the change can be reflected is they are updating the user
  const changingCommissionType = () => {
    state.userCommission.commission.commission_percentage = 0
    state.userCommission.commission.flat_commission = 0
    state.userCommission.commission.commission_effective_date = null
  }

  const emptyUser = {
    first_name: "",
    last_name: "",
    display_name: "",
    email: "",
    phone: "",
    role: ""
  }

  const emptyCommission = {
    flat_commission: 0,
    commission_percentage: 0,
    commission_effective_date: null
  }

  const state = reactive({
    loading: false,
    user: cloneDeep(emptyUser),
    userCommission: {
      user: cloneDeep(emptyUser),
      commission: cloneDeep(emptyCommission)
    },
    originalUser: null,
    originalCommission: null,
    roles: [],
    selected_role_label: "",
    is_percentage: true,
    roles_rates: [],
    shirts: [
      { name: "XS", value: "XS" },
      { name: "S", value: "S" },
      { name: "M", value: "M" },
      { name: "L", value: "L" },
      { name: "XL ", value: "XL" },
      { name: "2XL", value: "2XL" },
      { name: "3XL", value: "3XL" },
      { name: "4XL", value: "4XL" },
      { name: "5XL", value: "5XL" }
    ],
    team_leads: [],
    sales_managers_and_directors: [],
    is_sales_agent: false
  })

  const rules = computed(() => ({
    userCommission: {
      user: {
        first_name: { required, $lazy: true },
        last_name: { required, $lazy: true },
        email: { required, email, $lazy: true }
      }
    }
  }))

  const v$ = useVuelidate(rules, state)

  const resetUser = () => {
    let userCommission = {
      user: null,
      commission: null
    }
    if (userProp) {
      userCommission.user = userService.dtoUser(userProp)
      userCommission.commission = userService.dtoCommission(userProp)
      state.originalUser = cloneDeep(userCommission.user)
      state.originalCommission = cloneDeep(userCommission.commission)
    } else {
      userCommission.user = emptyUser
      userCommission.commission = emptyCommission
      state.originalUser = cloneDeep(userCommission.user)
      state.originalCommission = cloneDeep(userCommission.commission)
      state.userCommission.user = cloneDeep(userCommission.user)
      v$.value.$reset()
      state.loading = false
    }
    state.userCommission.commission = userCommission.commission
    state.userCommission.user = userCommission.user
  }
  const createUpdateUser = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }

    state.loading = true
    if (state.userCommission.user.id) {
      // We always want the commission fields in the user object to be present in the case that they are updated
      let requestData = {
        user: {},
        commission: {}
      }

      requestData.user = $removeUnusedProps(
        state.userCommission.user,
        state.originalUser
      )

      // here we are looking to see if anything has changed in the commission fields
      requestData.commission = $removeUnusedProps(
        state.userCommission.commission,
        state.originalCommission
      )
      // if there is something there, indicating that there was a change, we will send the whole object
      if (requestData.commission) {
        requestData.commission.commission_effective_date =
          state.userCommission.commission.commission_effective_date
        requestData.commission.commission_percentage =
          state.userCommission.commission.commission_percentage
        requestData.commission.flat_commission =
          state.userCommission.commission.flat_commission
        requestData.commission.commission_effective_date = new Date(
          requestData.commission.commission_effective_date
        )
        requestData.commission.rental_total_flat_commission_rate =
          state.userCommission.commission.rental_total_flat_commission_rate
        // requestData.commission.rental_effective_rate =
        //   state.userCommission.commission.rental_effective_rate;
      }

      /*
    if(requestData.commission){
      if(requestData.commission.commission_percentage > 45 || requestData.commission.commission_percentage < 0){
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Comission percentage must be between 0 and 45",
          group: "br",
          life: 5000,
        });
        state.loading = false;
        return
      }
    }*/

      if (requestData.commission) {
        if (requestData.commission.rental_effective_rate > 200) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Rental effective rate must be at most 200.",
            group: "br",
            life: 5000
          })
          state.loading = false
          return
        }
      }

      if (requestData.user.phone) {
        requestData.user.phone = requestData.user.phone.replace(/-/g, "")
      }

      if (!$isObjectPopulated(requestData)) {
        toast.add({
          severity: "warn",
          summary: "User Unchanged",
          detail: "User Unchanged",
          group: "br",
          life: 5000
        })
        return
      }

      const { data, error } = await userApi.updateUser(
        state.userCommission.user.id,
        requestData
      )

      if (!isAdmin) {
        userStore.setCurrentUser(userService.dtoUser(data.value))
        await userService.setCurrentUserFromAuthUser()
        await userService.updateAbility($ability)
      }

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "User Updated",
          detail: "Successfully updated user",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating user",
          group: "br",
          life: 5000
        })
      }
      swapOldUser(data.value)
      state.loading = false
    } else {
      if (state.userCommission.commission) {
        /*
      if(state.userCommission.commission.commission_percentage > 45 || state.userCommission.commission.commission_percentage < 0){
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Comission percentage must be between 0 and 45",
          group: "br",
          life: 5000,
        });
        state.loading = false;
        return
      }*/

        if (state.userCommission.rental_effective_rate > 200) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Rental effective rate must be at most 200.",
            group: "br",
            life: 5000
          })
          state.loading = false
          return
        }
      }

      const { data, error } = await userApi.createUser(state.userCommission)

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "User Created",
          detail: "Successfully saved user",
          group: "br",
          life: 5000
        })
      } else {
        toast.add({
          severity: "warn",
          summary: "The email already exists",
          detail: "The email already exists",
          group: "br",
          life: 5000
        })
        state.loading = false
        return
      }

      let updatedUsers = cloneDeep(userStore.users)
      updatedUsers.unshift(userService.dtoUser(data.value))
      userStore.setUsers(updatedUsers.map((u) => userService.dtoUser(u)))
      resetUser()
    }
    state.loading = false
    emit("hide")
  }

  watch(
    () => state.userCommission.user.role_id,
    async (newVal, oldVal) => {
      if (isCreate.value) {
        for (var i = 0; i < state.roles_rates.length; i++) {
          if (
            state.userCommission.user.role_id == state.roles_rates[i].role_id
          ) {
            state.userCommission.commission.commission_percentage =
              state.roles_rates[i].sales_commission_rate
          }
        }
      }
    }
  )

  watch(
    () => state.userCommission.user.role_id,
    async (newVal, oldVal) => {
      const sales_agent_role = userStore.roles.filter(
        (r) => r.name.toLowerCase() == "sales_agent"
      )
      state.is_sales_agent =
        state.userCommission.user.role_id == sales_agent_role[0].id
    }
  )
</script>

<style></style>
