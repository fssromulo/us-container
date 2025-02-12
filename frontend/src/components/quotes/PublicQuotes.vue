<template>
  <div class="flex justify-center flex-wrap">
    <div class="flex justify-center flex-wrap w-full">
      <div>
        <img
          src="/images/blocks/bbb.png"
          alt="footer sections"
          width="100"
          height="50"
          class="mr-4"
        />
      </div>
      <div class="col-span-12">
        <div class="flex justify-center flex-wrap">
          <a :href="cms.facebook_link" v-if="cms.facebook_link">
            <img
              src="/images/blocks/facebook.png"
              alt="footer sections"
              width="40"
              height="40"
              class="mr-8"
            />
          </a>
          <a :href="cms.instagram_link" v-if="cms.instagram_link">
            <img
              src="/images/blocks/instagram.png"
              alt="footer sections"
              width="40"
              height="40"
              class="mr-8"
            />
          </a>
          <a :href="cms.youtube_link" v-if="cms.youtube_link">
            <img
              src="/images/blocks/youtube.png"
              alt="footer sections"
              width="40"
              height="40"
              class="mr-8"
            />
          </a>
        </div>
      </div>

      <div class="flex justify-center flex-wrap">
        <Button
          label="Container dimensions"
          @click="containerDimensions"
          class="p-button-secondary p-button-sm sm:w-auto w-full"
        ></Button>
      </div>
      <div class="flex justify-center flex-wrap">
        <Button
          label="How to order"
          @click="howToOrderLink"
          class="p-button-secondary p-button-sm sm:w-auto w-full ml-4"
        ></Button>
      </div>

      <div class="col-span-12">
        <p class="text-3xl flex justify-center flex-wrap">
          Container Accessories & Rentals
        </p>
      </div>
      <div class="border border-t opacity-50 mb-2 col-span-12"></div>
      <div class="flex justify-center flex-wrap">
        <div class="grid grid-cols-12 gap-4">
          <div class="col-span-6">
            <Button
              v-if="cms.accessories_link !== null"
              label="Accessories"
              @click="openAccessorriesLink"
              class="p-button-secondary p-button-rounded w-full mr-4 pr-8"
            ></Button>
          </div>
          <div class="col-span-6">
            <Button
              v-if="cms.rto_link"
              label="Rentals"
              @click="openRentLink"
              class="p-button-secondary p-button-rounded w-full ml-2"
            ></Button>
          </div>
        </div>
      </div>
      <div class="col-span-12">
        <p class="flex justify-center flex-wrap text-3xl"> How we deliver </p>
      </div>
      <!-- embed youtube video -->
      <iframe
        :class="smAndSmaller ? 'w-10' : 'w-6'"
        height="315"
        src="https://www.youtube.com/embed/vJniz5ucKsM"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
      ></iframe>
    </div>
  </div>
</template>

<script setup>
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import { onMounted } from "vue"

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger

  const { cms } = defineProps({
    cms: {
      type: Object,
      required: true
    }
  })

  onMounted(() => {
    insertGoogleScript()
  })

  const insertGoogleScript = () => {
    console.log("inserting google script (PublicQuotes.vue)")
    const googleAdScript = document.createElement("script")

    googleAdScript.innerHTML = `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  })(window,document,'script','dataLayer','');`

    window.document.body.appendChild(googleAdScript)
    const googleIframeScript = document.createElement("noscript")
    googleIframeScript.innerHTML = `<iframe src="https://www.googletagmanager.com/ns.html?id=" height="0" width="0" style="display:none;visibility:hidden"></iframe>`
    window.document.body.appendChild(googleIframeScript)
  }

  const howToOrderLink = () => {
    window.open("https://usacontainers.co/how-to-order-online/", "_blank")
  }

  const containerDimensions = () => {
    window.open("https://usacontainers.co/inventory/", "_blank")
  }

  const openAccessorriesLink = () => {
    window.open(cms.accessories_link, "_blank")
  }
  const openRentLink = () => {
    window.open(state.cms.rto_link, "_blank")
  }
</script>
