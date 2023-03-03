<template>
  <div class="text-center">
    <div class="card text-center">
<!--      <img src="/shawa.jpg" class="card-img-top" alt="...">-->
      <div class="card-body">
        <h5>Заказ успешен!</h5>
        <div v-html="message"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "SuccessView",
  params: ["error"],
  computed: {
    message: function() {
      if(this.$route.query.error === "bot") {
        return 'Однако бот не смог отправить вам сообщение.<br/>Откройте диалог с ботом <a href="https://t.me/shawarmaasaservice_bot">@shawarmaasaservice_bot</a> и нажмите кнопку СТАРТ.'
      }
      return "Бот выслал вам сообщение с деталями заказа."
    }
  },
  created() {

  }
}
</script>

<style scoped>
.card {
        margin: 0 auto; /* Added */
        float: none; /* Added */
        margin-bottom: 10px; /* Added */
}
</style>