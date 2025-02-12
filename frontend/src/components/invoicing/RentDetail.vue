<template>
  <section class="flex flex-col w-full">
    <ConfirmPopup></ConfirmPopup>

    <div class="flex items-center justify-between w-full">
      <p class="mt-0 mb-0 text-xl font-semibold text-900 dark:text-0">
        <span class=""> Order Info </span>
      </p>
      <Button
        type="button"
        :disabled="!creditCardFeeToggleEnabled"
        class="p-button p-component p-button-primary"
        @click="handleOrderSettingsUpdate"
        >Other Order Settings</Button
      >
      <Button
        type="button"
        icon="pi pi-pencil text-sm"
        class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
        @click="handleEditClick"
      ></Button>
    </div>
    <div class="col-span-12 mt-4 border border-t"></div>
    <table v-if="state.order">
      <tbody>
        <tr
          v-if="!state.isEditing && !state.order.type === 'RENT'"
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Created On</td>
          <td class="text-xl text-900 dark:text-0">
            {{ state.order.created_at }}
          </td>
        </tr>

        <!-- Delivered On -->
        <tr
          v-if="state.isEditing || state.order.calculated_delivered_at"
          style="height: 2rem"
        >
          <td
            v-if="state.isEditing || state.order.calculated_delivered_at"
            class="text-xl text-700 dark:text-100"
          >
            Delivered On
          </td>
          <td
            v-if="!state.isEditing && state.order.calculated_delivered_at"
            class="text-xl text-900 dark:text-0"
          >
            {{ dfc(state.order.calculated_delivered_at) }}
          </td>
          <td
            v-if="
              state.isEditing && $ability.can('update', 'order-delivered_at')
            "
          >
            <DatePicker
              style="width: 210px"
              showIcon
              showButtonBar
              v-model="state.order.calculated_delivered_at"
              dateFormat="mm/dd/y"
              id="delivered_on"
              class="text-xl"
            ></DatePicker>
            <Button
              v-tooltip="
                'Changing this date will cause a cascade effect for the due on date for all future periods.'
              "
              icon="pi pi-info-circle"
              class="text-yellow-600 bg-transparent border-0"
            />
          </td>
        </tr>

        <!-- Paid Thru -->
        <tr
          v-if="!state.isEditing && state.order.calculated_paid_thru"
          style="height: 2rem"
        >
          <td class="text-base text-xl text-700 dark:text-100">Paid Thru</td>
          <td
            v-if="state.order.calculated_paid_thru"
            class="text-base text-xl text-900 dark:text-0"
          >
            {{ state.order.calculated_paid_thru || "" }}
          </td>
        </tr>
        <tr v-if="!state.isEditing">
          <td class="text-base text-xl text-700 dark:text-100"
            >Current Rent Balance</td
          >
          <td class="text-base text-xl text-900 dark:text-0">
            {{ $fc(state.order.calculated_rent_balance) }}
          </td>
        </tr>
        <tr v-if="!state.isEditing" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100"> Rent Subtotal </td>
          <td
            v-if="!state.isEditing || state.order.type === 'RENT_TO_OWN'"
            class="text-base text-xl text-900 dark:text-0"
          >
            {{ $fc(state.order.calculated_monthly_subtotal) }}
          </td>
        </tr>
        <tr
          style="height: 2rem"
          v-if="$ability.can('update', 'order_column-tax') && !state.isEditing"
        >
          <td class="text-xl text-700 dark:text-100"> Rent Tax </td>
          <td
            v-if="!state.isEditing && state.order.rent_periods.length"
            class="text-xl text-900 dark:text-0"
          >
            {{
              $fc(
                state.order.rent_periods.length >= 2
                  ? state.order.rent_periods[1]?.calculated_rent_period_tax
                  : state.order.rent_periods[0]
                      ?.calculated_rent_period_tax_without_downpayment
              )
            }}
          </td>
        </tr>

        <tr style="height: 2rem" v-if="!state.isEditing">
          <td class="text-xl text-700 dark:text-100">Rent total</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{ $fc(calculateRentTotal(state.order.rent_periods, state.order)) }}
          </td>
        </tr>

        <tr v-if="!state.isEditing" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Fees</td>
          <td class="text-xl text-900 dark:text-0">
            {{ $fc(state.order.calculated_fees) }}
          </td>
        </tr>

        <tr style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Status</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{
              filteredStatusOptions?.find((o) => o.value === state.order.status)
                ?.label
            }}
          </td>
          <td v-else>
            <Select
              :disabled="!$ability.can('update', 'order_column-status')"
              v-model="state.order.status"
              scrollHeight="330px"
              :options="
                allowedStatusOptions.filter((e) => {
                  if (
                    state.order.status === 'Partially Paid' ||
                    state.order.status === 'Invoiced'
                  ) {
                    if (
                      state.order.status === 'Partially Paid' &&
                      state.order.calculated_remaining_order_balance == 0
                    ) {
                      return e.value !== 'Partially Paid'
                    } else {
                      return e.value !== 'Paid' && e.value !== 'Partially Paid'
                    }
                  }
                  if (e.value == 'On Rent') {
                    return false
                  }

                  return true
                })
              "
              optionLabel="label"
              optionValue="value"
            />
          </td>
        </tr>

        <tr style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Rent Due On Day</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{ state.order.rent_due_on_day ?? "None" }}
          </td>

          <td v-if="state.isEditing" class="flex text-xl text-900 dark:text-0">
            <InputNumber v-model="state.order.rent_due_on_day" />
            <Button
              v-tooltip="
                'Changing this date will cause a cascade effect for the due on date for all future periods.'
              "
              icon="pi pi-info-circle"
              class="text-yellow-600 bg-transparent border-0"
            />
          </td>
        </tr>

        <!-- Driver Paid On -->
        <tr
          v-if="state.isEditing || state.order.calculated_delivered_at"
          style="height: 2rem"
        >
          <td
            v-if="state.isEditing || state.order.completed_at"
            class="text-xl text-700 dark:text-100"
          >
            Driver Paid On
          </td>
          <td
            v-if="!state.isEditing && state.order.completed_at"
            class="text-xl text-900 dark:text-0"
          >
            {{ state.order.completed_at }}
          </td>
          <td
            v-if="
              state.isEditing &&
              $ability.can('update', 'order-completed_at') &&
              state.order.total_paid > 0
            "
          >
            <DatePicker
              style="width: 210px"
              showIcon
              showButtonBar
              v-model="state.order.completed_at"
              dateFormat="mm/dd/y"
              id="driver_paid_on"
              class="text-xl"
            >
            </DatePicker>
          </td>
        </tr>

        <tr v-if="!state.isEditing" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Team lead</td>
          <td class="text-xl text-900 dark:text-0">
            {{ state.team_lead }}
          </td>
        </tr>

        <tr v-if="!state.isEditing" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Manager</td>
          <td class="text-xl text-900 dark:text-0">
            {{ state.orderUser?.assistant?.manager?.full_name || "N/A" }}
          </td>
        </tr>

        <!-- Agent -->
        <tr style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Agent</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{ state.order?.user?.full_name }}
          </td>
          <td @click="getUsers" v-else>
            <Select
              style="width: 210px"
              :disabled="!$ability.can('update', 'order_column-agent_email')"
              filter
              v-model="state.order.user_id"
              :placeholder="state.order?.user?.full_name"
              :options="mappedUsers"
              optionLabel="label"
              optionValue="value"
              :loading="state.loadingUsers"
            />
          </td>
        </tr>

        <tr
          v-if="
            !state.isEditing &&
            state.order.type !== 'PURCHASE' &&
            state.order.type !== 'PURCHASE_ACCESSORY'
          "
        >
          <td class="text-xl text-700 dark:text-100">Card on File</td>
          <td class="text-xl text-900 dark:text-0">{{ cardOnFile }}</td>
        </tr>
        <tr
          v-if="
            !state.isEditing &&
            state.order.type !== 'PURCHASE' &&
            state.order.type !== 'PURCHASE_ACCESSORY'
          "
        >
          <td class="text-xl text-700 dark:text-100">ACH on File</td>
          <td class="text-xl text-900 dark:text-0" v-if="props.hasAch">
            {{ props.bankName }} - R {{ props.routingNumber }} - A
            {{ props.accountNumber }}
          </td>
          <td class="text-xl text-900 dark:text-0" v-else>No ACH on file</td>
        </tr>
        <tr
          v-if="userStore.cms?.account_name !== 'USA Containers'"
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Purchase Order Job Id</td>
          <td v-if="state.isEditing" class="text-xl text-900 dark:text-0">
            <InputText
              v-model="state.order.purchased_order_job_id"
              type="text"
            />
          </td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{ state.order.purchased_order_job_id }}
          </td>
        </tr>
        <tr
          v-if="userStore.cms?.account_name !== 'USA Containers'"
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Purchase Order Number</td>
          <td v-if="state.isEditing" class="text-xl text-900 dark:text-0">
            <InputText
              v-model="state.order.purchase_order_number"
              type="text"
            />
          </td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{ state.order.purchase_order_number }}
          </td>
        </tr>
        <tr
          v-if="
            state.isEditing &&
            userStore.cms?.applications[
              customerStore.order.type.toLowerCase()
            ] == true
          "
        >
          <td class="text-xl text-700 dark:text-100">Application Type</td>
          <td>
            <Select
              v-model="state.order.customer_application_schema_id"
              :modelValue="state.order?.customer_application_schema?.id"
              style="height: 40px"
              icon="pi pi-plus"
              class="w-full mt-1"
              optionLabel="name"
              optionValue="value"
              placeholder="Select application type"
              :options="state.application_schemas"
            />
          </td>
        </tr>

        <tr
          v-if="
            $ability.can('read', 'order_column-gateway_cost') &&
            !state.isEditing &&
            state.order.type !== 'RENT' &&
            state.order.charge_gateway_cost
          "
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Gateway cost</td>
          <td class="text-xl text-900 dark:text-0">
            {{ $fc(state.order.calculated_gateway_cost) }}
          </td>
        </tr>
        <tr v-if="!state.isEditing" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Misc. Costs</td>
          <td class="text-xl text-900 dark:text-0">
            {{ $fc(state.order.calculated_misc_costs) }}
          </td>
        </tr>
        <tr v-if="!state.isEditing" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Created On</td>
          <td class="text-xl text-900 dark:text-0">
            {{ state.order.created_at }}
          </td>
        </tr>

        <tr
          v-if="
            state.isEditing && $ability.can('update', 'order_column-misc_cost')
          "
          style="height: 2rem"
        >
          <OrderAlterations
            :itemsProp="state.order.misc_cost"
            :isEditing="state.isEditing"
            amountFieldName="amount"
            categoryFieldName="cost_type"
            categoryFieldName2="id"
            placeholderText="Select a cost type"
            :handleDeleteClickFunc="handleDeleteMiscCostClick"
            :closeConfirmationToastFunc="closeConfirmationToast"
            :freshDictAorAdd="freshMiscCostDict"
            addButtonText="Add Cost(s)"
            :isLoading="state.isLoading"
            :handleAddItemSaveClickFunc="handleAddMiscCostSaveClick"
            :showConfirmToast="showConfirmToast"
            :headingName="headersDict.miscCost"
          />
        </tr>
      </tbody>
    </table>

    <div class="flex flex-col items-center mt-2">
      <UpdateOrderSettings
        v-if="state.isEditing"
        :attributes="state.order.attributes"
        :order="state.order"
        @updated-attributes="setAttributes"
      />

      <Button
        v-if="hasInventory"
        severity="primary"
        label="Move Out"
        style="max-width: 200px"
        @click="state.moveOutContainer = true"
        class="mt-2"
      ></Button>
      <Button
        severity="primary"
        label="REMOVE RUSH FEE"
        style="max-width: 200px"
        v-if="hasRushFees"
        class="mt-2"
        :loading="state.isRemoving"
        @click="removeRushFee($event)"
      ></Button>
      <div v-else>
        <Button
          v-for="rush in rush_options"
          :key="rush.label"
          severity="primary"
          :label="rush.label"
          style="margin-left: 30px"
          @click="displayRushFee(rush.fee)"
        ></Button>
      </div>

      <Button
        v-if="canViewHistory"
        severity="primary"
        label="See history"
        style="max-width: 200px"
        class="mt-2"
        @click="getContainerHistory()"
      ></Button>
    </div>
    <div v-if="state.isEditing" class="col-span-12 mt-2 border border-t"></div>
    <div class="grid grid-cols-12 gap-4 text-right">
      <div class="col-span-4 col-start-5">
        <Button
          v-if="state.isEditing"
          @click="toggleEdit"
          label="Cancel"
          class="p-button-raised p-button-secondary"
        />
      </div>
      <div class="col-span-4">
        <Button
          v-if="state.isEditing"
          @click="saveOrder"
          :loading="state.isLoading"
          class="p-button-raised"
          label="Save"
        />
      </div>
    </div>
  </section>
  <Dialog
    v-model:visible="state.displayApplyDiscounts"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ maxWidth: '1100px' }"
    header="Discounts"
    :modal="true"
    class="p-fluid"
  >
    <CouponsDiscounts />
  </Dialog>
  <Dialog
    v-model:visible="state.displayRushFee"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ maxWidth: '1100px' }"
    :header="state.rush_fee == 0 ? `RUSH FREE` : `RUSH FEE`"
    :modal="true"
    class="p-fluid"
  >
    <RushFee
      :order_id="state.order.id"
      :resetFunc="resetAfterRushFee"
      :rush_fee="state.rush_fee"
    />
  </Dialog>
  <Dialog
    v-model:visible="state.addContainerNumberDialog"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ maxWidth: '1100px' }"
    header="Add container number"
    :modal="true"
    class="p-fluid"
  >
    <AddContainerNumber
      @containerNumberAdded="saveOrder(false)"
      :lineItems="customerStore.order.line_items"
    />
  </Dialog>
  <Dialog
    v-model:visible="state.addPaymentModal"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ maxWidth: '1100px' }"
    header="Add Payment"
    :modal="true"
    class="p-fluid"
  >
    <OrderDetailPaymentType
      @paymentAdded="transactionUpdate"
      :orderDetail="state.order"
    />
  </Dialog>

  <Dialog
    v-model:visible="state.orderSettingsUpdate"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ maxWidth: '1100px' }"
    header="Order Settings Update"
    :modal="true"
    class="p-fluid"
  >
    <EditOrderSettings
      :order="state.order"
      :saveOrder="saveOrder"
      @hide="state.orderSettingsUpdate = false"
    />
  </Dialog>
  <Dialog
    v-model:visible="state.displayHistory"
    maximizable
    dismissableMask
    closeOnEscape
    :style="{ maxWidth: '1100px' }"
    header="Containers history"
    :modal="true"
    class="p-fluid"
  >
    <div v-for="(obj, index) in state.rental_history" :key="index">
      <ContainerHistory
        :key="obj.id"
        :inventoryHistory="obj"
        :container="obj"
      />
    </div>
  </Dialog>
  <Dialog
    v-model:visible="state.moveOutContainer"
    modal
    dismissableMask
    closeOnEscape
    :breakpoints="{
      '2000px': '45vw',
      '1400px': '55vw',
      '1200px': '65vw',
      '992px': '75vw',
      '600px': '100vw',
      '480px': '100vw',
      '320px': '100vw'
    }"
  >
    <template #header>
      <div
        class="flex items-center justify-between p-4 border-b border-gray-200"
      >
        <p class="text-3xl font-semibold">Move out containers</p>
      </div>
    </template>

    <template #default>
      <div class="p-6">
        <div class="space-y-4">
          <!-- Row for each line item -->
          <div
            v-for="(line_item, index) in filteredLineItems"
            :key="index"
            class="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
          >
            <div class="flex-1 text-gray-700 text-md dark:text-gray-100">
              {{
                container(
                  line_item.inventory?.container_number,
                  line_item.inventory?.container_release_number
                )
              }}
            </div>
            <div class="flex-1">
              <DatePicker
                v-model="state.rental_move_out_date[line_item.id]"
                id="scheduled_date"
                class="w-full ml-1 text-md"
                placeholder="Set Move Out Date"
                dateFormat="mm/dd/y"
              />
            </div>
            <div class="flex justify-end flex-1">
              <button
                :disabled="!state.rental_move_out_date[line_item.id]"
                @click="
                  detachRentalContainer(line_item.inventory?.id, line_item.id)
                "
                :class="[
                  'px-4 py-2 rounded bg-blue-500 text-white hover:bg-blue-600',
                  { 'opacity-50': !state.rental_move_out_date[line_item.id] }
                ]"
              >
                Move Out (Single)
              </button>
            </div>
          </div>

          <!-- "Move out all" row -->
          <div
            v-if="filteredLineItems.length > 1"
            class="flex items-center justify-between p-4 border-t border-gray-200"
          >
            <div class="flex-1 text-xl font-semibold">Move out all</div>
            <div class="flex-1">
              <DatePicker
                v-model="state.override_move_out_date"
                id="scheduled_date"
                class="w-full ml-1 text-md"
                placeholder="Set Move Out Date"
                dateFormat="mm/dd/y"
              />
            </div>
            <div class="flex justify-end flex-1">
              <button
                :disabled="!state.override_move_out_date"
                @click="detachRentalContainer()"
                :class="[
                  'px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600',
                  { 'opacity-50': !state.override_move_out_date }
                ]"
              >
                Move All Out
              </button>
            </div>
          </div>

          <div
            class="flex items-center justify-between p-4 border-t border-gray-200"
          >
            <div class="font-semibold text-md"
              >Remaining balance (based on move out dates):
              <span>{{
                state.isCalculatingRemainingBalance
                  ? "Calculating..."
                  : $fc(state.remaining_balance)
              }}</span>
            </div>
            <div v-if="hasDownpaymentNote" class="text-red-500"
              >*Note: Has the customer paid the pickup or delivery fees? Please
              check.</div
            >
          </div>
        </div>
      </div>
    </template>
  </Dialog>
  <Toast position="bottom-center" group="bc" :visible.sync="state.showToast">
    <template #message="slotProps">
      <div class="flex flex-col items-center" style="flex: 1">
        <div class="text-center">
          <i class="pi pi-exclamation-triangle" style="font-size: 3rem"></i>
          <div class="my-4 text-xl font-bold">
            {{ slotProps.message.summary }}
          </div>
        </div>
        <div class="flex gap-2">
          <Button
            severity="success"
            label="Yes"
            :loading="state.isLoading"
            @click="state.toastConfirmAction"
          ></Button>
          <Button
            severity="secondary"
            label="No"
            @click="state.toastCancelAction"
          ></Button>
        </div>
      </div>
    </template>
  </Toast>
</template>

<script setup>
  import { reactive, onMounted, inject, computed } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import { dfl, dfc, dfa, convertDateForPost } from "@/service/DateFormat.js"
  import { useUsers } from "@/store/modules/users"
  import AddContainerNumber from "../inventory/AddContainerNumber.vue"
  import EditOrderSettings from "../invoicing/rent/EditOrderSettings.vue"
  import CreditCardReading from "./CreditCardReading.vue"
  import OrderAlterations from "./OrderAlterations.vue"
  import OrderDetailPaymentType from "./payment/OrderDetailPaymentType.vue"
  import UsersService from "@/service/User"
  import UserApi from "@/api/user"
  import CustomerService from "@/service/Customers"
  import CustomerApi from "@/api/customers"
  import isEqual from "lodash.isequal"
  import UpdateOrderSettings from "./create/UpdateOrderSettings.vue"
  import CouponsDiscounts from "./create/CouponsDiscounts.vue"
  import RushFee from "./create/RushFee.vue"
  import ContainerHistory from "../inventory/ContainerHistory.vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useToast } from "primevue/usetoast"
  import { ref, watch } from "vue"
  import AccountService from "@/service/Account.js"
  import { DateTime } from "luxon"
  import LineItemApi from "@/api/lineItem"
  import { useConfirm } from "primevue/useconfirm"
  import PaymentMethodsApi from "@/api/payment_methods"

  const paymentMethodsApi = new PaymentMethodsApi()
  const confirm = useConfirm()
  const toast = useToast()
  const usersStore = useUsers()
  const lineItemApi = new LineItemApi()
  const customerApi = new CustomerApi()
  const $ability = inject("$ability")
  const customerStore = useCustomerOrder()
  const accountService = new AccountService()
  const $isObjectPopulated = inject("$isObjectPopulated")
  const $fc = inject("$formatCurrency")
  const $removeUnusedProps = inject("$removeUnusedProps")
  const userStore = useUsers()
  const usersService = new UsersService()
  const userApi = new UserApi()
  const customerService = new CustomerService()
  const disabledStatusDays = ref([15])
  const currentDate = new Date()

  const props = defineProps({
    swapCustomerOrder: {},
    routingNumber: { default: "" },
    hasAch: { default: false },
    hasCreditCard: { default: false },
    accountNumber: { default: "" },
    bankName: { default: "" }
  })

  const emit = defineEmits(["updateRentPeriods"])

  const markAsSettled = async (target, inventory_id, line_item_id) => {
    let downpayment_note = null
    customerStore.order.note.forEach((el) => {
      if (el.title == "downpayment_note") {
        downpayment_note =
          "Has the customer paid the pickup or delivery fees? Please check." +
          el.content
      }
    })
    if (downpayment_note == null) {
      moveOut(inventory_id, line_item_id)
    } else {
      confirm.require({
        target: event.target,
        message: downpayment_note,
        icon: "pi pi-info-circle",
        acceptClass: "p-button-danger p-button-sm",
        accept: async () => {
          moveOut(inventory_id, line_item_id)
        },
        reject: () => {
          toast.add({
            severity: "error",
            summary: "Canceled",
            detail: "Container(s) move out canceled",
            life: 2000
          })
          state.detachContainerLoading = false
        }
      })
    }
  }

  const moveOut = async (inventory_id, line_item_id) => {
    state.isLoading = true
    let updateData = {
      lineItems:
        line_item_id != "All"
          ? [
              {
                id: line_item_id,
                inventory_id: null,
                product_cost: 0
              }
            ]
          : state.line_item_list,
      move_out_date:
        line_item_id != "All"
          ? state.rental_move_out_date[line_item_id]
          : state.override_move_out_date,
      move_out_type: line_item_id == "All" ? "All" : "Single",
      inventoryIdsToMakeAvailable:
        inventory_id != "All" ? [inventory_id] : state.inventory_list,
      is_move_out: true
    }

    const { data, error } = await lineItemApi.updateLineItemExtra(updateData)

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error updating order",
        group: "br",
        life: 2000
      })
      state.isLoading = false
      return
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Detached container",
        group: "br",
        life: 2000
      })
      await updateOrder()
      props.swapCustomerOrder(state.order.id)
      state.isLoading = false
      state.moveOutContainer = false
    }
  }

  const detachRentalContainer = async (
    inventory_id = "All",
    line_item_id = "All"
  ) => {
    let options =
      line_item_id == "All" ? " all these container(s)" : "this container"

    confirm.require({
      target: event.target,
      message:
        customerStore.order?.calculated_rent_balance > 0
          ? `Do you want to move out ${options} with balance ${$fc(
              state.remaining_balance
            )} ?`
          : `Do you want to move out ${options} ?`,
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        await markAsSettled(event.target, inventory_id, line_item_id)
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Canceled",
          detail: "Container(s) move out canceled",
          life: 2000
        })
        state.detachContainerLoading = false
      }
    })
  }

  const removeRushFee = async (event) => {
    confirm.require({
      target: event.currentTarget,
      message: "Do you want remove rush fee ?",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        state.isRemoving = true
        const { error } = await customerApi.removeRushFee(state.order.id)
        if (error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: "Error removing rush fee",
            group: "br",
            life: 2000
          })
          state.isRemoving = false
          return
        }
        await updateOrder()
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Rush fee removed",
          group: "br",
          life: 2000
        })
        state.isRemoving = false
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Rejected",
          detail: "You have rejected",
          life: 2000
        })
      }
    })
  }

  const hasRushFees = computed(() => {
    return (
      state.order.fees.filter((e) => {
        return e.fee_type == "RUSH"
      }).length > 0
    )
  })

  const hasDownpaymentNote = computed(() => {
    return (
      customerStore.order.note.filter((e) => {
        return e.title == "downpayment_note"
      }).length > 0
    )
  })

  const isLastDayOfMonth = () => {
    const currentDay = currentDate.getDate()
    const lastDayOfMonth = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth() + 1,
      0
    ).getDate()

    return currentDay === lastDayOfMonth
  }

  const calculateRentTotal = () => {
    const { rent_periods, calculated_monthly_subtotal } = state.order

    let calculated_rent
    if (rent_periods.length >= 2) {
      calculated_rent = rent_periods[1].calculated_rent_period_tax
    } else {
      calculated_rent =
        rent_periods[0]?.calculated_rent_period_tax_without_downpayment || 0
    }

    return calculated_rent + calculated_monthly_subtotal
  }

  const isNotAllowedStatusDay = () => {
    const dayOfMonth = currentDate.getDate()

    if (userStore.cms?.allow_deliveries_marked_on_15th_and_last_day_of_month) {
      return false
    }

    return disabledStatusDays.value.includes(dayOfMonth) || isLastDayOfMonth()
  }

  const is_always_autopay = computed(() => {
    if (userStore.cms?.is_only_auto_pay_allowed) {
      return true
    }
    return false
  })

  const allowedStatusOptions = computed(() => {
    let paymentStatus = ["Paid", "Delayed"]
    if ($ability.can("update", "only_order_payment-status")) {
      return filteredStatusOptions.value.filter((e) =>
        paymentStatus.includes(e.value)
      )
    }
    return filteredStatusOptions.value
  })

  const filteredStatusOptions = computed(() => {
    if (state.order.type === "RENT") {
      if (!userStore.cms?.order_status_selection?.rentalStatusOptions) {
        return userStore.cms?.order_status_options?.rentalStatusOptions
      } else {
        return userStore.cms?.order_status_selection?.rentalStatusOptions
      }
    } else if (state.order.type === "RENT_TO_OWN") {
      if (!userStore.cms?.order_status_selection?.rentToOwnStatusOptions) {
        return userStore.cms?.order_status_options?.rentToOwnStatusOptions
      } else {
        return userStore.cms?.order_status_selection?.rentToOwnStatusOptions
      }
    } else if (
      state.order.type === "PURCHASE" ||
      state.order.type === "PURCHASE_ACCESSORY"
    ) {
      if (!userStore.cms?.order_status_selection?.salesStatusOptions) {
        return userStore.cms?.order_status_options?.salesStatusOptions
      } else {
        return userStore.cms?.order_status_selection?.salesStatusOptions
      }
    }
  })

  const cardOnFile = computed(() => {
    if (!customerStore.order?.credit_card_number?.length) {
      return "No card on file"
    } else if (customerStore.order?.credit_card_number) {
      return customerStore.order?.credit_card_number.substring(
        customerStore.order?.credit_card_number.length - 4
      )
    }
    if (!customerStore.order?.credit_card.length) {
      return "No card on file"
    }
    const sortedTransactions = customerStore.order?.credit_card?.sort(
      (a, b) => {
        return new Date(b.created_at) - new Date(a.created_at)
      }
    )
    let latestTransaction = sortedTransactions[0]
    let merchant = latestTransaction?.merchant
    let number = latestTransaction?.response_from_gateway?.number
    return `${merchant} -- ${number}`
  })

  const creditCardFeeToggleEnabled = computed(() => {
    return usersStore.cms?.credit_card_fees.enable_toggle_credit_card_fees
  })

  const sorttedRentPeriod = computed(() => {
    return state.order.rent_periods.sort((a, b) => {
      const start_date_luxon_a = DateTime.fromISO(a.start_date)
      const start_date_luxon_b = DateTime.fromISO(b.end_date)
      return start_date_luxon_a - start_date_luxon_b
    })
  })

  const change_rental_period_due_date = async () => {
    state.isLoading = true
    let all_period_ids = sorttedRentPeriod.value.map((period) => period.id)
    const currentIndex = all_period_ids.indexOf(
      state.order.current_rent_period.id
    )
    let subsequent_periods = all_period_ids.slice(currentIndex + 1) || []
    const { error, data } = await customerApi.updateRentPeriodDueDate(
      {
        date: new Date(
          state.order.current_rent_period.start_date
        ).toLocaleDateString("en-US"),
        id: state.order.current_rent_period.id,
        order_id: state.order.id,
        rent_due_on_day: state.order.rent_due_on_day
      },
      subsequent_periods
    )

    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Updated rent period due date",
        group: "br",
        life: 5000
      })
      resetOrder()
    }
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to update rent period due date",
        group: "br",
        life: 5000
      })
    }
    state.isLoading = false
  }

  const getUser = async () => {
    if (state.order?.user?.id != null) {
      const { data } = await userApi.getUserById(state.order?.user?.id)
      state.orderUser = data.value
    }
  }

  const handleOrderSettingsUpdate = () => {
    state.orderSettingsUpdate = true
  }

  const handleEditClick = () => {
    if (isNotAllowedStatusDay()) {
      toast.add({
        severity: "warn",
        summary: "Warning",
        detail:
          "On the 15th or the last day of the month The Delivered and Completed status are restricted",
        group: "br",
        life: 7000
      })
    }
    toggleEdit()
  }

  const miscCostHeader = "Misc. Costs"
  const headersDict = {
    miscCost: miscCostHeader
  }

  const freshMiscCostDict = {
    amount: 0,
    cost_type: null
  }

  const handleAddMiscCostSaveClick = () => {
    const transformMiscCost = (item) => {
      let returnObj = {
        cost_type_id: item.cost_type || "string",
        amount: item.amount || 0,
        order_id: state.order.id
      }
      return returnObj
    }

    const transformedMiscCosts =
      customerStore.addedOrderItems[miscCostHeader].map(transformMiscCost)

    state.isLoading = true
    customerApi
      .createMiscCost(transformedMiscCosts)
      .then((response) => {
        if (response.error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: response.error.value.response.data.detail,
            life: 3000,
            group: "br"
          })
          return
        }

        toast.add({
          severity: "success",
          summary: "Success",
          detail: `Successfully added ${customerStore.addedOrderItems[miscCostHeader].length} misc cost(s)`,
          life: 3000,
          group: "br"
        })
      })
      .finally(() => {
        close()
        getOrderByDisplayId(state.order.display_order_id)
        customerStore.setAddedOrderItems(miscCostHeader, [])
        state.isEditing = true
      })
  }

  const canViewHistory = computed(() => {
    if (
      customerStore.order?.status.toLowerCase() == "invoiced" ||
      customerStore.order?.status.toLowerCase() == "quote" ||
      customerStore.order?.status.toLowerCase() == "estimate"
    ) {
      return false
    }
    if (customerStore.order?.calculated_rent_balance == 0) {
      return false
    }
    if (!customerStore.order.line_items.every((l) => l?.inventory)) {
      return false
    }
    return true
  })

  const container = (container_number, container_release_number) => {
    if (
      container_number !== undefined &&
      container_number !== "" &&
      container_release_number !== undefined &&
      container_release_number !== ""
    ) {
      return container_number + " | " + container_release_number
    } else if (container_number !== undefined && container_number !== "") {
      return container_number
    } else {
      return container_release_number
    }
  }

  const handleDeleteMiscCostClick = (misc_cost_id) => {
    state.isLoading = true
    customerApi
      .deleteMiscCost(misc_cost_id)
      .then((response) => {
        if (response.error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: response.error.value.response.data.detail,
            life: 3000,
            group: "br"
          })
          return
        }
        toast.add({
          severity: "success",
          summary: "Success",
          detail: `Successfully deleted`,
          life: 3000,
          group: "br"
        })
      })
      .finally(() => {
        closeConfirmationToast()
        close()
        getOrderByDisplayId(state.order.display_order_id)
        state.isEditing = true
      })
  }

  const getOrderByDisplayId = async (id) => {
    const { data, isLoading, error } = await customerApi.getOrderByDisplayId(id)

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading order",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      customerStore.setOrder(null)
      customerStore.setOrder(data.value)
    }
  }

  const closeConfirmationToast = () => {
    hideConfirmToast("bc")
  }

  const showConfirmToast = (confirmFunction, cancelfunction) => {
    toast.add({
      severity: "warn",
      summary: "Are you sure?",
      detail: "Proceed to confirm",
      group: "bc"
    })
    state.toastConfirmAction = confirmFunction
    state.toastCancelAction = cancelfunction
  }

  const hideConfirmToast = (group) => {
    toast.removeGroup(group)
  }

  const getUsers = async () => {
    if (userStore.users.length === 0) {
      state.loadingUsers = true
      const { data } = await userApi.getUsers()
      userStore.setUsers(data.value.map((u) => usersService.dtoUser(u)))
      state.loadingUsers = false
    }
  }

  const applicationOverrideToggleEnabled = computed(() => {
    return (
      (usersStore.cms?.applications?.rent &&
        customerStore.order.type === "RENT") ||
      (usersStore.cms?.applications?.purchase &&
        (customerStore.order.type === "PURCHASE" ||
          customerStore.order.type === "PURCHASE_ACCESSORY")) ||
      (usersStore.cms?.applications?.rent_to_own &&
        customerStore.order.type === "RENT_TO_OWN")
    )
  })

  const mappedUsers = computed(() => {
    return userStore.users
      .filter((u) => {
        if (
          userStore.currentUser.permissions.includes("update:all_order_agents")
        ) {
          return true
        } else {
          return (
            userStore.currentUser.manager
              .map((u) => u.assistant.id)
              .includes(u.id) || userStore.currentUser.id === u.id
          )
        }
      })
      .map((user) => {
        return {
          label: user.full_name,
          value: user.id
        }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const filteredLineItems = computed(() => {
    return customerStore.order.line_items.filter((e) => e.inventory !== null)
  })

  const statusChangedToDeliveryOrCompleted = (
    containerNumberNotAdded = true
  ) => {
    if (containerNumberNotAdded) {
      state.addContainerNumberDialog = true
      return false
    }
    if (!customerStore.order.line_items.every((l) => l?.inventory)) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Must have all containers attached",
        life: 3000,
        group: "br"
      })
      state.order.status = cloneDeep(state.originalOrder.status)
      return false
    }
    if (
      state.originalOrder.status !== "Delivered" &&
      state.order.status === "Delivered"
    ) {
      state.addContainerNumberDialog = true
    }
    if (
      state.order?.is_pickup &&
      state.order.status === "Completed" &&
      state.originalOrder.status !== "Completed"
    ) {
      state.addContainerNumberDialog = true
    }
  }

  const setAttributes = (attributes) => {
    state.order.attributes = attributes
  }

  const hasInventory = computed(() => {
    return (
      customerStore.order.line_items.filter(
        (e) => e.inventory != null && e.inventory?.id != ""
      ).length > 0
    )
  })

  const resetOrder = () => {
    let order = customerService.orderDto()
    state.originalOrder = cloneDeep(order)
    state.order = cloneDeep(order)
    state.order.customer_application_schema_id =
      state.order?.customer_application_schema?.id || null
    state.line_item_list = filteredLineItems.value.map((e) => {
      return {
        id: e.id,
        inventory_id: null,
        product_cost: 0
      }
    })
    state.inventory_list = filteredLineItems.value.map((e) => {
      return e.inventory?.id
    })
  }

  const close = () => {
    state.isLoading = false
    state.isEditing = false
    state.addContainerNumberDialog = false
    state.discountApplied = false
    state.addPayment = null
  }

  onMounted(async () => {
    resetOrder()
    await getUser()
    state.isRborTaxChanged = false

    const { data, error } = await userApi.getTeamMemberLeadById(
      customerStore.order?.user?.id
    )
    if (data.value) {
      state.team_lead = data.value?.first_name + " " + data.value?.last_name
    }

    state.remaining_balance = customerStore.order.calculated_rent_balance
  })

  const toggleEdit = async () => {
    state.isEditing = !state.isEditing
    for (let key in headersDict) {
      customerStore.setAddedOrderItems(headersDict[key], [])
    }

    const result = await customerApi.getApplicationSchemasByName(
      customerStore.order.type,
      state.order.id
    )
    if (result.data.value) {
      state.application_schemas = result.data.value.map((el) => {
        return {
          name: el.full_schema_name,
          value: el.id
        }
      })
    }
  }

  const transactionUpdate = async (data) => {
    state.addPaymentModal = false
    state.isEditing = false
  }

  const saveOrder = async (containerNumberNotAdded = true) => {
    state.isLoading = true
    state.addPaymentModal = false
    let isOrderSame =
      isEqual(state.order, state.originalOrder) && !state.addPayment

    if (isOrderSame) {
      toast.add({
        severity: "warn",
        summary: "Warn",
        detail: "Order unchanged",
        group: "br",
        life: 2000
      })
      state.isLoading = false
      return
    }
    let isRentDueOnDayChanged = !isEqual(
      state.order.rent_due_on_day,
      state.originalOrder.rent_due_on_day
    )

    if (state.order.status === "Delivered" && containerNumberNotAdded) {
      if (!state.order.line_items.every((l) => l?.inventory)) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Must have all containers attached",
          life: 3000,
          group: "br"
        })
        state.isLoading = false
        return
      }

      const canChangeStatus = statusChangedToDeliveryOrCompleted(
        containerNumberNotAdded
      )
      if (!canChangeStatus) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Must have all containers attached",
          life: 3000,
          group: "br"
        })
        return
      }
    }
    if (!containerNumberNotAdded) {
      state.addContainerNumberDialog = false
    }

    const requestData = $removeUnusedProps(state.order, state.originalOrder)
    const miscRequestData = $removeUnusedProps(
      state.order.misc_cost,
      state.originalOrder.misc_cost
    )

    if (requestData.delivered_at != undefined) {
      requestData.delivered_at = convertDateForPost(requestData.delivered_at)
    }

    if (requestData.completed_at != undefined) {
      requestData.completed_at = convertDateForPost(requestData.completed_at)
    }

    delete requestData["misc_cost"]

    let miscRequestDataArray = []
    miscRequestDataArray = Object.values(miscRequestData).map((cost) => ({
      id: cost.id,
      amount: cost.amount,
      cost_type_id: cost.cost_type.id
    }))

    let feeAmtIddict = {}
    for (let i = 0; i < state.order.fees.length; i++) {
      let diff = $removeUnusedProps(
        state.order.fees[i],
        state.originalOrder.fees[i]
      )
      let newAmt = state.order.fees[i].fee_amount
      let originalAmt = state.originalOrder.fees[i].fee_amount
      if (Object.keys(diff).length !== 0) {
        if (newAmt !== originalAmt) {
          feeAmtIddict[state.order.fees[i].id] = {
            order_balance_change: newAmt - originalAmt
          }
        } else {
          feeAmtIddict[state.order.fees[i].id] = {
            order_balance_change: 0
          }
        }
      }
    }

    state.isLoading = true
    let isWorking = false

    if (miscRequestDataArray.length !== 0) {
      isWorking = true
      customerApi.updateMiscCost(miscRequestDataArray).then((response) => {
        if (response.error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: response.error.value.response.data.detail,
            life: 3000,
            group: "br"
          })
          return
        } else {
          isWorking = false
          toast.add({
            severity: "success",
            summary: "Success",
            detail: "Misc Cost updated",
            group: "br",
            life: 2000
          })
        }
      })
    }

    if (isRentDueOnDayChanged) {
      await change_rental_period_due_date()
    }

    if (!isOrderSame) {
      const previousStateOrder = state.order
      try {
        delete requestData["fees"]
        const response = await customerApi.updateOrder(
          state.order.id,
          requestData
        )
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Order updated",
          group: "br",
          life: 2000
        })
        customerStore.setOrder(null)
        customerStore.setOrder(response.data)

        if (requestData["status"] == "Paid") {
          await customerApi.gtrack(
            userStore.currentUser.id,
            customerStore.order.id
          )
        } else if (state.addPayment >= previousStateOrder.remaining_balance) {
          await customerApi.gtrack(
            userStore.currentUser.id,
            customerStore.order.id
          )
        } else if (previousStateOrder.remaining_balance == 0) {
          await customerApi.gtrack(
            userStore.currentUser.id,
            customerStore.order.id
          )
        }
      } finally {
        if (!isWorking) {
          close()
          props.swapCustomerOrder(state.order.id)
        }
      }
    } else {
      close()
      props.swapCustomerOrder(state.order.id)
    }
    if (isRentDueOnDayChanged) {
      emit("updateRentPeriods", {}, true)
    }
    state.isLoading = false
  }

  const state = reactive({
    order: {},
    isCalculatingRemainingBalance: false,
    orderUser: null,
    quickSearchOrder: [],
    originalOrder: {},
    loadingUsers: false,
    addPayment: null,
    isEditing: false,
    isLoading: false,
    addContainerNumberDialog: false,
    discountApplied: false,
    addedMiscCosts: [],
    toastConfirmAction: null,
    toastCancelAction: null,
    showToast: false,
    costTypeOptions: ref([]),
    isEditRb: true,
    isRborTaxChanged: false,
    notes: "",
    application_schemas: [],
    orderSettingsUpdate: false,
    rent_due_on_day: null,
    addPaymentModal: false,
    displayApplyDiscounts: false,
    displayRushFee: false,
    rush_fee: null,
    moveOutContainer: false,
    line_item_list: [],
    inventory_list: [],
    rental_move_out_date: {},
    override_move_out_date: null,
    displayHistory: false,
    rental_history: [],
    remaining_balance: 0
  })

  const rush_options = computed(() => {
    if (userStore.cms?.rush) {
      return (
        Object.values(userStore.cms?.rush || {})?.filter((rush) => {
          if (rush.permission == "") {
            return true
          }
          return $ability.can(rush.action, rush.permission)
        }) || []
      )
    }
    return []
  })

  const updateOrder = async () => {
    const { data } = await customerApi.getOrderByDisplayId(
      customerStore.order.display_order_id
    )
    customerStore.setOrder(null)
    customerStore.setOrder(data.value)
  }

  const resetAfterRushFee = async () => {
    await getOrderByDisplayId(state.order.display_order_id)
    state.displayRushFee = false
  }

  const displayRushFee = (rush_fee) => {
    state.displayRushFee = true
    state.rush_fee = rush_fee
  }

  const getContainerHistory = async () => {
    state.displayHistory = true
    const { data } = await customerApi.getOrderLineItemsHistory(
      customerStore.order.id
    )
    state.rental_history = data.value
  }

  watch(
    () => customerStore.order,
    (newVal) => {
      if (newVal !== null && newVal !== undefined) resetOrder()
    },
    { immediate: true, deep: true }
  )

  watch(
    () => state.isEditing,
    () => {
      resetOrder()
    }
  )

  watch(
    () => state.rental_move_out_date,
    async () => {
      if (Object.keys(state.rental_move_out_date).length > 0) {
        state.isCalculatingRemainingBalance = true
        await calculate_remaining_balance()
        state.isCalculatingRemainingBalance = false
      }
    },
    { immediate: true, deep: true }
  )

  watch(
    () => state.order.calculated_order_tax,
    () => {
      if (
        state.order.calculated_order_tax !=
        state.originalOrder.calculated_order_tax
      ) {
        state.isEditRb = false
        state.isRborTaxChanged = true
      } else {
        state.isRborTaxChanged = false
      }
    }
  )

  watch(
    () => state.order.calculated_remaining_order_balance,
    () => {
      if (
        state.order.calculated_remaining_order_balance !=
        state.originalOrder.calculated_remaining_order_balance
      ) {
        state.isEditRb = true
        state.isRborTaxChanged = true
      } else {
        state.isRborTaxChanged = false
      }
    }
  )

  const calculate_remaining_balance = async () => {
    const dataReq = {
      move_out_dates: state.rental_move_out_date
    }
    const { data, error } = await customerApi.calculate_remaining_balance(
      dataReq,
      state.order.id
    )
    state.remaining_balance = data.value
  }
</script>

<style scoped>
  .p-datepicker-current-day {
    background-color: blue !important;
  }
</style>
