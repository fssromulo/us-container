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
        >Update Order Settings</Button
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
        <tr v-if="!state.isEditing" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Created On</td>
          <td class="text-xl text-900 dark:text-0">
            {{ state.order.created_at }}
          </td>
        </tr>

        <!-- Paid On -->
        <tr
          v-if="
            state.order.type !== 'RENT' &&
            (state.isEditing || state.order.paid_at)
          "
          style="height: 2rem"
        >
          <td
            v-if="state.isEditing || state.order.paid_at"
            class="text-xl text-700 dark:text-100"
          >
            Paid In Full On
          </td>
          <td
            v-if="!state.isEditing && state.order.paid_at"
            class="text-xl text-900 dark:text-0"
          >
            {{ dfc_without_zone(state.order.calculated_paid_in_full_date) }}
          </td>
          <td
            v-if="
              state.isEditing &&
              $ability.can('update', 'order-paid_at') &&
              state.order.total_paid > 0
            "
          >
            <DatePicker
              style="width: 210px"
              showIcon
              showButtonBar
              v-model="state.order.paid_at"
              dateFormat="mm/dd/y"
              id="paid_on"
              class="text-xl"
            ></DatePicker>
          </td>
        </tr>
        <!-- Signed At -->
        <tr
          v-if="
            state.order.type !== 'RENT' &&
            (state.isEditing || state.order.signed_at)
          "
          style="height: 2rem"
        >
          <td
            v-if="state.isEditing || state.order.signed_at"
            class="text-xl text-700 dark:text-100"
          >
            Signed At
          </td>
          <td
            v-if="!state.isEditing && state.order.signed_at"
            class="text-xl text-900 dark:text-0"
          >
            {{
              state.order.signed_at != "Invalid DateTime"
                ? state.order.signed_at
                : ""
            }}
          </td>
          <!-- <td
          v-if="
            state.isEditing &&
            (userStore.currentUser?.role_name === 'admin' ||
              userStore.currentUser?.role_name === 'superadmin')
          "
        >
          <DatePicker
            style="width: 210px"
            showIcon
            showButtonBar
            v-model="state.order.signed_at"
            dateFormat="mm/dd/y"
            id="paid_on"
            class="text-xl"
          ></DatePicker>
        </td> -->
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
          </td>
        </tr>

        <tr v-if="!state.isEditing && state.order.type === 'RENT'">
          <td class="text-base text-xl text-700 dark:text-100"
            >Current Rent Balance</td
          >
          <td class="text-base text-xl text-900 dark:text-0">
            {{ $fc(state.order.calculated_rent_balance) }}
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
              $ability.can('update', 'order-total_paid') &&
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
        <!-- <tr v-if="!state.isEditing" style="height: 2rem">
        <td class="text-xl text-700 dark:text-100">Type</td>
        <td class="text-xl text-900 dark:text-0">
          {{ state.order.type }}
        </td>
      </tr> -->

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
              style="width: 210px"
              :disabled="!$ability.can('update', 'order_column-status')"
              v-model="state.order.status"
              scrollHeight="330px"
              :options="
                allowedStatusOptions.filter((e) => {
                  if (state.order.type == 'RENT_TO_OWN') {
                    return true
                  }

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
        <!-- Payment Type -->
        <tr
          v-if="
            !state.isEditing &&
            state.order.payment_type &&
            state.order.type !== 'RENT'
          "
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Payment Type</td>
          <td class="text-xl text-900 dark:text-0">
            {{ state.order.payment_type }}
          </td>
        </tr>

        <tr v-if="!state.isEditing && !isPurchase">
          <td class="text-xl text-700 dark:text-100">Card on File</td>
          <td class="text-xl text-900 dark:text-0" v-if="props.hasCreditCard">{{
            cardOnFile
          }}</td>
          <td class="text-xl text-900 dark:text-0" v-else> False </td>
        </tr>
        <tr v-if="!state.isEditing && !isPurchase">
          <td class="text-xl text-700 dark:text-100">ACH on File</td>
          <td class="text-xl text-900 dark:text-0" v-if="props.hasAch">
            {{ props.bankName }} - R {{ props.routingNumber }} - A
            {{ props.accountNumber }}
          </td>
          <td class="text-xl text-900 dark:text-0" v-else>No ACH on file</td>
        </tr>

        <tr
          v-if="
            state.isEditing &&
            !isPurchase &&
            $ability.can('update', 'order_column-remaining_balance')
          "
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Payment Type</td>
          <td class="text-sm text-900 dark:text-0">
            <template
              v-if="
                state.isEditing &&
                $ability.can('update', 'order_column-remaining_balance')
              "
            >
              <Select
                style="width: 210px"
                v-model="state.order.payment_type"
                class="text-xl"
                :options="paymentOptions"
                placeholder="Select a payment type"
                scrollHeight="330px"
                optionLabel="label"
                optionValue="value"
              />
            </template>
          </td>
          <td>
            <div class="col-span-6 mb-4 field">
              <Textarea
                v-model="state.notes"
                :autoResize="true"
                rows="2"
                placeholder="Payment Notes"
                label="Notes"
                cols="10"
              />
            </div>
          </td>
        </tr>

        <tr
          v-if="
            state.isEditing &&
            isPurchase &&
            $ability.can('update', 'order_column-remaining_balance') &&
            state.order.calculated_remaining_order_balance > 0
          "
          class="mt-1 mb-1"
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Add Payment</td>
          <td class="text-sm text-900 dark:text-0">
            <Button
              v-if="
                state.isEditing &&
                $ability.can('update', 'order_column-remaining_balance')
              "
              label="Add Payment"
              v-tooltip="'Add a payment record to this order'"
              class="text-green-600 bg-transparent border-0"
              @click="addPaymentModal"
            />
          </td>
        </tr>

        <tr
          v-if="
            state.isEditing &&
            !isPurchase &&
            $ability.can('update', 'order_column-remaining_balance') &&
            state.order.type !== 'RENT'
          "
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Add Payment</td>
          <td class="">
            <InputNumber
              style="width: 210px"
              mode="currency"
              currency="USD"
              v-model="state.addPayment"
              id="tax"
              type="text"
              class="flex-1"
            />
          </td>
        </tr>
        <tr v-if="!state.isEditing" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Subtotal</td>
          <td
            v-if="
              (!state.isEditing && state.order.type === 'RENT') ||
              state.order.type === 'RENT_TO_OWN'
            "
            class="text-base text-xl text-900 dark:text-0"
          >
            {{ $fc(state.order.calculated_monthly_subtotal) }}
          </td>
          <td
            v-if="!state.isEditing && isPurchase"
            class="text-xl text-900 dark:text-0"
          >
            {{ $fc(state.order.calculated_sub_total_price) }}
          </td>
        </tr>
        <tr
          v-if="!state.isEditing && state.order.type !== 'RENT'"
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Fees</td>
          <td class="text-xl text-900 dark:text-0">
            {{ $fc(state.order.calculated_fees) }}
          </td>
        </tr>

        <tr
          style="height: 2rem"
          v-if="$ability.can('update', 'order_column-tax')"
        >
          <td class="text-xl text-700 dark:text-100">
            {{ state.order.type === "RENT" ? "Rent Tax" : "Estimated Tax" }}
          </td>
          <td
            v-if="!state.isEditing && state.order.type !== 'RENT'"
            class="text-xl text-900 dark:text-0"
          >
            {{ $fc(state.order.calculated_order_tax) }}
          </td>
          <td
            v-if="state.isEditing && state.order.type !== 'RENT'"
            class="text-xl text-900 dark:text-0"
          >
            <InputNumber
              mode="currency"
              currency="USD"
              v-model="state.order.calculated_order_tax"
              id="tax"
              type="text"
              class="flex-1"
              :disabled="state.isEditRb && state.isRborTaxChanged"
            />
          </td>

          <td
            v-if="
              !state.isEditing &&
              state.order.type === 'RENT' &&
              state.order.rent_periods.length
            "
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
          <td
            v-if="
              state.isEditing &&
              state.order.type === 'RENT' &&
              state.order.rent_periods.length
            "
            class="text-xl text-900 dark:text-0"
          >
            <InputNumber
              mode="currency"
              currency="USD"
              v-model="
                state.order.rent_periods[0]
                  .calculated_rent_period_tax_without_downpayment
              "
              id="tax"
              type="text"
              class="flex-1"
            />
          </td>
        </tr>

        <tr style="height: 2rem" v-if="state.order.type == 'RENT'">
          <td class="text-xl text-700 dark:text-100">Rent total</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{
              $fc(
                (state.order.rent_periods.length >= 2
                  ? state.order.rent_periods[1].calculated_rent_period_tax
                  : state.order.rent_periods[0]
                      ?.calculated_rent_period_tax_without_downpayment) ||
                  0 + state.order.calculated_monthly_subtotal
              )
            }}
          </td>
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
        <tr v-if="!state.isEditing && isPurchase" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Total Price</td>
          <td class="text-xl text-900 dark:text-0">
            {{ $fc(state.order.calculated_total_price) }}
          </td>
        </tr>
        <tr
          v-if="
            !state.isEditing &&
            state.order.type === 'RENT' &&
            state.order.rent_periods.length
          "
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">First Payment Due</td>
          <td class="text-xl text-900 dark:text-0">
            {{
              $fc(
                state.order.rent_periods[0]
                  ?.calculated_rent_period_total_balance
              )
            }}
          </td>
        </tr>
        <tr v-if="!state.isEditing && isPurchase" style="height: 2rem">
          <td class="text-xl text-700 dark:text-100">Total Customer Paid</td>
          <td class="text-xl text-900 dark:text-0">
            {{ $fc(state.order.total_paid) }}
          </td>
        </tr>
        <tr
          style="height: 2rem"
          v-if="
            $ability.can('update', 'order_column-remaining_balance') &&
            state.order.type !== 'RENT'
          "
        >
          <td v-if="!state.isEditing" class="text-xl text-700 dark:text-100">
            Remaining Balance
          </td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{
              $fc(
                state.order.calculated_remaining_order_balance < 0
                  ? 0
                  : state.order.calculated_remaining_order_balance
              )
            }}
          </td>
          <!-- <td v-if="state.isEditing" class="text-xl text-900 dark:text-0">
          <InputNumber
            mode="currency"
            currency="USD"
            v-model="state.order.calculated_remaining_order_balance"
            id="tax"
            type="text"
            class="flex-1"
            :disabled="!state.isEditRb && state.isRborTaxChanged"
          />
        </td> -->
        </tr>
        <tr
          v-if="!state.isEditing && creditCardFeeToggleEnabled"
          class="text-xl text-900 dark:text-0"
        >
          <td class="text-xl text-700 dark:text-100">Allow External Payment</td>
          <td class="text-xl text-900 dark:text-0">
            {{ state.order.allow_external_payments ? "Yes" : "No" }}
          </td>
        </tr>
        <tr
          v-if="!state.isEditing && creditCardFeeToggleEnabled"
          class="col-span-12"
        >
          <td class="text-xl text-700 dark:text-100"
            >Credit card fee enabled</td
          >
          <td class="text-xl text-900 dark:text-0">
            {{ state.order.credit_card_fee ? "Yes" : "No" }}
          </td>
        </tr>
        <tr
          v-if="!state.isEditing && state.order.type === 'RENT'"
          style="height: 2rem"
        >
          <td class="text-base text-xl text-700 dark:text-100">Is Auto Pay</td>
          <td
            v-if="!state.isEditing"
            class="text-base text-xl text-900 dark:text-0"
          >
            {{ state.order.is_autopay ? "Yes" : "No" }}
          </td>
        </tr>

        <tr
          v-if="
            !state.isEditing &&
            state.order.payment_type &&
            state.order.type === 'RENT'
          "
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Apply Late Fee</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{ state.order.is_late_fee_applied ? "Yes" : "No" }}
          </td>
        </tr>

        <!-- CUSTOM DATE AFTER APPROVAL -->
        <!-- <tr v-if="state.order.type === 'RENT'" style="height: 2rem">
        <td class="text-xl text-700 dark:text-100">Set Delivery Date</td>
        <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
          {{ state.order.has_delivery_date_set ? "Yes" : "No" }}
        </td>

        <td v-if="state.isEditing" class="text-xl text-900 dark:text-0">
          <ToggleSwitch
            v-model="state.order.has_delivery_date_set"
            type="text"
          />
          <Button
            v-show="state.order.customer_profile_id === null"
            v-tooltip="
              'Toggle to set contract start date at a specific number of days from date of approval or not'
            "
            icon="pi pi-info-circle"
            class="text-red-600 bg-transparent border-0"
          />
        </td>
      </tr> -->

        <tr
          v-if="!state.isEditing && applicationOverrideToggleEnabled"
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Application override</td>
          <td v-if="!state.isEditing" class="text-xl text-900 dark:text-0">
            {{ state.order.override_application_process ? "Yes" : "No" }}
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
          <td class="text-xl text-700">Processing cost</td>
          <td class="text-xl text-900">
            {{ $fc(state.order.calculated_processing_cost) }}
          </td>
        </tr>
        <tr
          v-if="
            !state.isEditing &&
            $ability.can('read', 'order_column-order_profit')
          "
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Total Order Profit</td>
          <td class="text-xl text-900 dark:text-0">
            {{ $fc(state.order.calculated_profit) }}
          </td>
        </tr>
        <tr
          v-if="
            !state.isEditing &&
            $ability.can('read', 'order_column-order_profit') &&
            state.order.type == 'PURCHASE_ACCESSORY'
          "
          style="height: 2rem"
        >
          <td class="text-xl text-700 dark:text-100">Accessory Commission</td>
          <td class="text-xl text-900 dark:text-0">
            {{ $fc(state.order.calculated_accessory_commission) }}
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
        <tr
          v-if="
            state.isEditing &&
            $ability.can('update', 'order_column-misc_fee') &&
            state.order.type !== 'RENT'
          "
          style="height: 2rem"
        >
          <OrderAlterations
            :itemsProp="state.order.fees"
            :isEditing="state.isEditing"
            amountFieldName="fee_amount"
            categoryFieldName="type"
            categoryFieldName2="id"
            placeholderText="Select a fee type"
            :handleDeleteClickFunc="handleDeleteFeeClick"
            :closeConfirmationToastFunc="closeConfirmationToast"
            :freshDictAorAdd="freshFeeDict"
            addButtonText="Add Fee(s)"
            :isLoading="state.isLoading"
            :handleAddItemSaveClickFunc="handleAddFeeSaveClick"
            :showConfirmToast="showConfirmToast"
            :headingName="headersDict.fee"
          />
        </tr>
      </tbody>
    </table>

    <div class="flex flex-wrap justify-center mt-8">
      <UpdateOrderSettings
        v-if="state.isEditing"
        :attributes="state.order.attributes"
        :order="state.order"
        @updated-attributes="setAttributes"
      />
    </div>
    <div class="flex flex-wrap justify-center mt-8">
      <Button
        v-if="state.order.type === 'RENT' && hasInventory"
        severity="primary"
        label="Move Out"
        @click="state.moveOutContainer = true"
      ></Button>

      <Button
        v-if="state.order.type !== 'RENT'"
        severity="primary"
        label="See Available Discounts"
        style="margin-left: 30px"
        @click="state.displayApplyDiscounts = true"
      ></Button>
      <Button
        severity="primary"
        label="REMOVE RUSH"
        style="margin-left: 30px"
        v-if="hasRushFees"
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
          @click="displayRushFee(rush.fee, rush.label, rush.message || '')"
        ></Button>
      </div>

      <Button
        v-if="canViewHistory"
        severity="primary"
        label="See history"
        style="margin-left: 30px"
        @click="getContainerHistory()"
      ></Button>
      <Button
        v-if="state.order.type == 'RENT_TO_OWN'"
        severity="primary"
        label="Send RTO Agent Email"
        style="margin-left: 30px"
        :loading="state.loadingSendAgentEmail"
        @click="sendAgentEmailRTO()"
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
    :header="state.rush_label"
    :modal="true"
    class="p-fluid"
  >
    <RushFee
      :order_id="state.order.id"
      :resetFunc="resetAfterRushFee"
      :rush_fee="state.rush_fee"
      :rush_message="state.rush_message"
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
      :lineItems="
        customerStore.order.line_items.filter(
          (li) => li.product_type !== 'CONTAINER_ACCESSORY'
        )
      "
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
  import { reactive, onMounted, onBeforeMount, inject, computed } from "vue"
  import cloneDeep from "lodash.clonedeep"
  import { dfl, dfc, dfa, dfc_without_zone } from "@/service/DateFormat.js"
  import { useUsers } from "@/store/modules/users"
  import AddContainerNumber from "../inventory/AddContainerNumber.vue"
  import EditOrderSettings from "../invoicing/rent/EditOrderSettings.vue"
  import CreditCardReading from "./CreditCardReading.vue"
  import OrderAlterations from "./OrderAlterations.vue"
  import OrderDetailPaymentType from "./payment/OrderDetailPaymentType.vue"
  import UsersService from "@/service/User"
  import UserApi from "@/api/user"
  import CustomerService from "@/service/Customers"
  import { defaultPaymentTypesDropDown } from "@/utils/paymentTypes"
  import CustomerApi from "@/api/customers"
  import isEqual from "lodash.isequal"
  import UpdateOrderSettings from "./create/UpdateOrderSettings.vue"
  import CouponsDiscounts from "./create/CouponsDiscounts.vue"
  let paymentOptions = defaultPaymentTypesDropDown()
  import RushFee from "./create/RushFee.vue"
  import ContainerHistory from "../inventory/ContainerHistory.vue"

  import { useCustomerOrder } from "@/store/modules/customerOrder"

  import { useToast } from "primevue/usetoast"
  import { ref, watch } from "vue"

  import AccountService from "@/service/Account.js"
  import { DateTime } from "luxon"
  import LineItemApi from "@/api/lineItem"
  import { useConfirm } from "primevue/useconfirm"
  import { changeCountry } from "@/utils/formatCurrency.js"
  import { convertDateForPost } from "@/service/DateFormat.js"
  import PaymentMethodsApi from "@/api/payment_methods"
  import { convertDateForPostRealDate } from "../../service/DateFormat"

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
  const disabledStatusDays = ref([15]) // In the future more days can be added here
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
    console.log(updateData)
    // return
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
  const isLastDayOfMonth = () => {
    const currentDay = currentDate.getDate()
    const lastDayOfMonth = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth() + 1,
      0
    ).getDate()

    return currentDay === lastDayOfMonth
  }
  const addPaymentModal = () => {
    state.addPaymentModal = true
  }
  const isNotAllowedStatusDay = () => {
    const dayOfMonth = currentDate.getDate()

    if (userStore.cms?.allow_deliveries_marked_on_15th_and_last_day_of_month) {
      return false
    }

    // Check if the current day is in the list of disabled days or the last day of the month
    return disabledStatusDays.value.includes(dayOfMonth) || isLastDayOfMonth()
  }

  const is_always_autopay = computed(() => {
    if (userStore.cms?.is_only_auto_pay_allowed) {
      return true
    }
    return false
  })

  // Computed property to generate filtered status options
  const allowedStatusOptions = computed(() => {
    let paymentStatus = ["Paid", "Delayed"]
    if ($ability.can("update", "only_order_payment-status")) {
      return filteredStatusOptions.value.filter((e) =>
        paymentStatus.includes(e.value)
      )
    }
    return filteredStatusOptions.value
  })

  const filter_not_aggregate = (lst) => {
    return lst.filter((el) => {
      if (el.is_aggregate == undefined) {
        return true
      }

      if (el.is_aggregate == true) {
        return false
      }

      return true
    })
  }

  const filteredStatusOptions = computed(() => {
    if (state.order.type === "RENT") {
      if (!userStore.cms?.order_status_selection?.rentalStatusOptions) {
        return filter_not_aggregate(
          userStore.cms?.order_status_options?.rentalStatusOptions
        )
      } else {
        return filter_not_aggregate(
          userStore.cms?.order_status_selection?.rentalStatusOptions
        )
      }
    } else if (state.order.type === "RENT_TO_OWN") {
      if (!userStore.cms?.order_status_selection?.rentToOwnStatusOptions) {
        return filter_not_aggregate(
          userStore.cms?.order_status_options?.rentToOwnStatusOptions
        )
      } else {
        return filter_not_aggregate(
          userStore.cms?.order_status_selection?.rentToOwnStatusOptions
        )
      }
    } else if (state.order.type === "PURCHASE") {
      if (!userStore.cms?.order_status_selection?.salesStatusOptions) {
        return filter_not_aggregate(
          userStore.cms?.order_status_options?.salesStatusOptions
        )
      } else {
        return filter_not_aggregate(
          userStore.cms?.order_status_selection?.salesStatusOptions
        )
      }
    } else if (state.order.type === "PURCHASE_ACCESSORY") {
      if (!userStore.cms?.order_status_selection?.accessorySalesStatusOptions) {
        return filter_not_aggregate(
          userStore.cms?.order_status_options?.accessorySalesStatusOptions
        )
      } else {
        return filter_not_aggregate(
          userStore.cms?.order_status_selection?.accessorySalesStatusOptions
        )
      }
    }
  })

  const cardOnFile = computed(() => {
    // get most recent by created_at
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
    state.orderSettingsUpdate = true //
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
  const feeHeader = "Fees"
  const headersDict = {
    miscCost: miscCostHeader,
    fee: feeHeader
  }

  const freshMiscCostDict = {
    // Set the 'amount' property to 'null'
    amount: 0,
    // Set the 'cost_type' property to an object with 'id' and 'name' properties, both initialized to 'null'
    cost_type: null
  }

  const freshFeeDict = {
    // Set the 'fee_amount' property to 'null'
    fee_amount: 0,
    // Set the 'fee_type' property to 'null'
    fee_type: null
  }

  /**
   * This function will handle the final click to save the recently added misc costs.
   * It will transform the to-be-added misc costs array to a dictionary that has the proper fields
   * for the post request to the backend
   * Then it will actually make the post request to create the given misc costs.
   * There is error handling via a message and then it will perform a clean up and reload of the
   * data. Finally it will bring the user right back to the editing screen so that they may continue
   * doing what they were working on.
   */
  const handleAddMiscCostSaveClick = () => {
    const transformMiscCost = (item) => {
      let returnObj = {
        cost_type_id: item.cost_type || "string", // Set a default value if cost_type is null
        amount: item.amount || 0, // Set a default value if amount is null
        order_id: state.order.id
      }
      return returnObj
    }
    // Transform each item in addedMiscCosts array
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
        close() // sets some tracking bools to false to reset the page
        getOrderByDisplayId(state.order.display_order_id) // this will cause the reload of the order so that it will reflect the changes made
        customerStore.setAddedOrderItems(miscCostHeader, []) // resets the to-be-added fields
        state.isEditing = true // takes the user right back to the editing screen so they may continue editing the order
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
  /**
   * This function will handle the final click to save the recently added fees.
   * It will transform the to-be-added misc costs array to a dictionary that has the proper fields
   * for the post request to the backend
   * Then it will actually make the post request to create the given misc costs.
   * There is error handling via a message and then it will perform a clean up and reload of the
   * data. Finally it will bring the user right back to the editing screen so that they may continue
   * doing what they were working on.
   */
  const handleAddFeeSaveClick = () => {
    state.isLoading = true
    const transformFee = (item) => {
      return {
        fee_type: "LATE", // Set a default value if cost_type is null
        type_id: item.type || "string", // Set a default value if cost_type is null
        fee_amount: item.fee_amount || 0, // Set a default value if amount is null
        order_id: state.order.id,
        due_at: null
      }
    }

    // Transform each item in addedMiscCosts array
    const transformedFees =
      customerStore.addedOrderItems[feeHeader].map(transformFee)

    customerApi
      .createFee(transformedFees)
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
          detail: `Successfully added ${customerStore.addedOrderItems[feeHeader].length} Fee(s)`,
          life: 3000,
          group: "br"
        })
      })
      .finally(() => {
        close() // sets some tracking bools to false to reset the page
        getOrderByDisplayId(state.order.display_order_id) // this will cause the reload of the order so that it will reflect the changes made
        customerStore.setAddedOrderItems(feeHeader, []) // resets the to-be-added fields
        state.isEditing = true // takes the user right back to the editing screen so they may continue editing the order
      })
  }

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

  /**
   * This function is used to delete a certain misc cost. This has error and success handling
   * via toast messages. Finally it will close the confirmation toast popup, and then reload the
   * screen for the user with all the new information
   * @param {string} misc_cost_id This is the given id of the misc cost that will be deleted
   */
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
        closeConfirmationToast() // closes the confirmation toast popup
        close() // sets some tracking bools to false to reset the page
        getOrderByDisplayId(state.order.display_order_id) // this will cause the reload of the order so that it will reflect the changes made
        state.isEditing = true // takes the user right back to the editing screen so they may continue editing the order
      })
  }

  /**
   * This function is used to delete a certain fee. This has error and success handling
   * via toast messages. Finally it will close the confirmation toast popup, and then reload the
   * screen for the user with all the new information
   * @param {string} fee_id This is the given id of the fee that will be deleted
   */
  const handleDeleteFeeClick = (fee_id) => {
    state.isLoading = true
    customerApi
      .deleteFee(fee_id)
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
        closeConfirmationToast() // closes the confirmation toast popup
        close() // sets some tracking bools to false to reset the page
        getOrderByDisplayId(state.order.display_order_id) // this will cause the reload of the order so that it will reflect the changes made
        state.isEditing = true // takes the user right back to the editing screen so they may continue editing the order
      })
  }

  /**
   * this function will repopulate the customerstore order object so that it is globally acceptable and updated. This is primarily used
   * to reload the editing screen so that the user can have a seemless experience
   * @param {*} id this is the display_order_id that comes from the order
   */
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

  /**
   * Simply hiding the toast popup message
   */
  const closeConfirmationToast = () => {
    hideConfirmToast("bc")
  }

  /**
   * This is a reusable function where you can create a popup toast notification where you also can pass it the yes and no functions
   * Anyone can call this function and then pass their custom confirm and cancel functions
   * @param {funciton} confirmFunction this function will be attached to the yes button for the popup
   * @param {function} cancelfunction this funtion will be attached to the no button for the popup
   */
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
  const rush_options = computed(() => {
    return (
      Object.values(userStore.cms?.rush || {})?.filter((rush) => {
        if (rush.permission == "") {
          return true
        }
        return $ability.can(rush.action, rush.permission)
      }) || []
    )
  })
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

  onBeforeMount(() => {
    let account_country = userStore.cms.account_country
    changeCountry(account_country)
  })

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

    const paymentMethodsData = await paymentMethodsApi.getAllPaymentMethods()
    paymentOptions = paymentMethodsData.data.value.map((el) => {
      return {
        label: el.display_name,
        value: el.name
      }
    })
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

  const transactionUpdate = async (data2) => {
    state.addPaymentModal = false
    state.isEditing = false
    const { data } = await customerApi.getOrderByDisplayId(
      state.order.display_order_id
    )
    if (data) {
      customerStore.setOrder(null)
      customerStore.setOrder(data.value)

      resetOrder()
    }
  }

  const saveOrder = async (containerNumberNotAdded = true) => {
    if (state.order.type === "PURCHASE_ACCESSORY") {
      containerNumberNotAdded = false
    }
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
      if (
        !state.order.line_items.every((l) => {
          if (l?.product_type !== "CONTAINER_ACCESSORY") {
            return l?.inventory
          }
          return true
        })
      ) {
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
    // This will be used for the save on the edit of any already existing misc costs. it will remove all of them that have not been modified
    const miscRequestData = $removeUnusedProps(
      state.order.misc_cost,
      state.originalOrder.misc_cost
    )

    // This will be used for the save on the edit of any already existing misc costs. it will remove all of them that have not been modified
    const feeRequestData = $removeUnusedProps(
      state.order.fees,
      state.originalOrder.fees
    )

    if (requestData.delivered_at != undefined) {
      requestData.delivered_at = convertDateForPostRealDate(
        new Date(requestData.delivered_at)
      ).toISOString()
    }

    if (requestData.completed_at != undefined) {
      requestData.completed_at = convertDateForPostRealDate(
        new Date(requestData.completed_at)
      )
    }

    if (requestData.paid_at != undefined) {
      requestData.paid_at = convertDateForPostRealDate(
        new Date(requestData.paid_at)
      ).toISOString()
    }

    delete requestData["misc_cost"] // do not want to edit this with this save order call. Only on the update misc cost call

    // converting object into an array so that it can fit the reqs of the api route
    let miscRequestDataArray = []
    miscRequestDataArray = Object.values(miscRequestData).map((cost) => ({
      id: cost.id,
      amount: cost.amount,
      cost_type_id: cost.cost_type.id
    }))

    // iterating over the feeRequestData to see if we have any differences btwn the amounts of the original and new

    let feeAmtIddict = {} // this dict will include all of the ids for the fees with altered amounts. the value
    // will equal whether its been altered or not
    for (let i = 0; i < state.order.fees.length; i++) {
      let diff = $removeUnusedProps(
        state.order.fees[i],
        state.originalOrder.fees[i]
      )
      let newAmt = state.order.fees[i].fee_amount
      let originalAmt = state.originalOrder.fees[i].fee_amount
      if (Object.keys(diff).length !== 0) {
        // if the fee amounts do not line up, then we will add the id into the list so that we can check it later
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

    // converting object into an array so that it can fit the reqs of the api route
    let feeRequestDataArray = []
    console.log(feeRequestData)
    feeRequestDataArray = Object.values(feeRequestData).map((fee) => ({
      id: fee.id,
      fee_amount: fee.fee_amount,
      fee_type: fee.fee_type,
      type_id: fee.type.id,
      order_balance_change: feeAmtIddict[fee.id].order_balance_change,
      order_id: state.order.id,
      updated_balance_change:
        fee.calculated_remaining_balance +
        feeAmtIddict[fee.id].order_balance_change
    }))

    state.isLoading = true
    let isWorking = false
    // this needs to come before the update order call, bc once this updates, then when the order gets repulled and populated
    // it will include these updated misc costs.
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

    if (feeRequestDataArray.length !== 0) {
      isWorking = true
      try {
        let response = await customerApi.updateFee(feeRequestDataArray)

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
            detail: "Fee(s) updated",
            group: "br",
            life: 2000
          })
        }
      } finally {
        if (isOrderSame && !isDiscountBeingApplied) {
          close()
          props.swapCustomerOrder(state.order.id) // Added to reload the note after adding one after a discount
        }
      }
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
        close()
        props.swapCustomerOrder(state.order.id) // Added to reload the note after adding one in a discount
      }
    } else {
      close()
      props.swapCustomerOrder(state.order.id) // Added to reload the note after adding one in a discount
    }
    if (isRentDueOnDayChanged) {
      emit("updateRentPeriods", {}, true)
    }
    state.isLoading = false
  }

  const state = reactive({
    order: {},
    orderUser: null,
    quickSearchOrder: [],
    originalOrder: {},
    loadingUsers: false,
    addPayment: null,
    isEditing: false,
    isLoading: false,
    addContainerNumberDialog: false,
    discountApplied: false,
    addedMiscCosts: [], // to-be-added misc costs that will be sent in a post request to the api
    addedFees: [], // to-be-added fees that will be sent in a post request to the api
    toastConfirmAction: null, // The action that will be tied to the yes button on the showtoast function
    toastCancelAction: null, // The action that will be tied to the no button on the showtoast function
    showToast: false, // bool that allows for the confirmation toast popup to be displayed
    costTypeOptions: ref([]), // This is the state object that actually holds and stores the cost_type options and then is used by miscCostOptionsList to populate the dropdown list
    isEditRb: true, // This will toggle the editing fields from being disabled or enabled for the remaining balance and tax fields. you cannot edit both fields at the same time
    isRborTaxChanged: false,
    notes: "",
    application_schemas: [],
    orderSettingsUpdate: false,
    rent_due_on_day: null,
    addPaymentModal: false,
    displayApplyDiscounts: false,
    displayRushFee: false,
    rush_label: "",
    rush_message: "",
    rush_fee: 150,
    moveOutContainer: false,
    line_item_list: [],
    inventory_list: [],
    rental_move_out_date: [],
    override_move_out_date: null,
    displayHistory: false,
    rental_history: [],
    loadingSendAgentEmail: false
  })
  const isPurchase = computed(() => {
    return (
      state.order.type === "PURCHASE" ||
      state.order.type === "PURCHASE_ACCESSORY"
    )
  })
  const sendAgentEmailRTO = async () => {
    state.loadingSendAgentEmail = true
    await customerApi.sendAgentEmailRTO(customerStore.order.id)
    state.loadingSendAgentEmail = false
  }

  const updateOrder = async () => {
    const { data } = await customerApi.getOrderByDisplayId(
      customerStore.order.display_order_id
    )
    customerStore.setOrder(null)
    customerStore.setOrder(data.value)
  }
  const displayRushFee = (rush_fee, header, message) => {
    state.displayRushFee = true
    state.rush_fee = rush_fee
    state.rush_label = header
    state.rush_message = message
  }
  const resetAfterRushFee = async () => {
    await getOrderByDisplayId(state.order.display_order_id)
    state.displayRushFee = false
    state.rush_fee = 0
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
</script>

<style scoped>
  .p-datepicker-current-day {
    background-color: blue !important;
  }
</style>
