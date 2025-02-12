<template>
  <div
    v-if="props.cms"
    class="bg-gray-900 px-6 py-6 md:px-12 lg:px-20 w-full"
    style="bottom: 0px; position: sticky"
  >
    <div class="bg-gray-900">
      <div class="grid grid-cols-12 gap-4">
        <div
          :class="
            !smAndSmaller
              ? 'col-span-12 md:col-span-3 md:mb-0 mb-4'
              : 'col-span-12 md:col-span-3 md:mb-0 mb-4 flex justify-center'
          "
        >
          <img
            src="/images/blocks/bbb.png"
            alt="footer sections"
            width="150"
            height="75"
            class="mr-4"
          />
        </div>
        <div
          class="col-span-12 md:col-span-3"
          v-if="props.cms.contact_us_link.length > 1"
        >
          <!-- <div
            class="text-white text-lg mb-6 flex flex-wrap"
            style="max-width: 290px"
          > -->
          <Button
            label="Contact us"
            @click="contactUs()"
            class="p-button-secondary p-button-sm sm:w-auto w-full"
          ></Button>
          <!-- </div> -->
          <div
            v-if="props.cms.terms_and_conditions_link.length > 1"
            :class="
              !smAndSmaller
                ? 'text-white mb-4 mt-4'
                : 'text-white mb-4 mt-4 flex justify-center'
            "
          >
            <a
              :href="props.cms.terms_and_conditions_link"
              class="underline decoration-solid text-white"
              >Terms & Conditions</a
            >
          </div>
        </div>
        <div
          class="text-gray-200 col-span-12 md:col-span-3"
          v-if="props.cms.customer_reviews_link.length > 1"
        >
          <Button
            label="Check reviews"
            @click="checkReviews()"
            class="p-button-secondary p-button-sm sm:w-auto w-full"
          ></Button>
        </div>
        <div
          :class="
            !smAndSmaller
              ? 'col-span-12 md:col-span-3'
              : 'col-span-12 md:col-span-3 flex justify-center mt-6'
          "
          class="text-gray-200"
        >
          <a :href="props.cms.facebook_link">
            <img
              src="/images/blocks/facebook.png"
              alt="footer sections"
              width="50"
              height="50"
              class="mr-8"
            />
          </a>
          <a :href="props.cms.instagram_link">
            <img
              src="/images/blocks/instagram.png"
              alt="footer sections"
              width="50"
              height="50"
              class="mr-8"
            />
          </a>
          <a :href="props.cms.youtube_link">
            <img
              src="/images/blocks/youtube.png"
              alt="footer sections"
              width="50"
              height="50"
              class="mr-8"
            />
          </a>
        </div>
      </div>
      <div class="flex justify-center flex-wrap">
        <div class="border border-t col-span-12"></div>

        <div class="text-white font-bold leading-none">
          {{ new Date().getFullYear() }} — {{ props.cms.account_name }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger

  const props = defineProps({
    cms: {
      type: Object,
      required: true
    }
  })

  const contactUs = () => {
    window.open(props.cms.contact_us_link, "_blank")
  }

  const checkReviews = () => {
    window.open(props.cms.customer_reviews_link, "_blank")
  }
</script>
