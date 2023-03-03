<template>
  <div class="text-center">
    <div class="card text-center">
<!--      <img src="/shawa.jpg" class="card-img-top" alt="...">-->
      <div class="card-body">
        <h5>Прием заказов уже закрыт!</h5>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ErrorView",

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