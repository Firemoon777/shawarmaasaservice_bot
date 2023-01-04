<template>
  <div class="text-center">
    <div class="card text-center">
<!--      <img src="/shawa.jpg" class="card-img-top" alt="...">-->
      <div class="card-body">
        <h5>Заказ успешен!</h5>
        Бот вышлет вам сообщение с деталями заказа.
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "SuccessView",

  methods: {

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