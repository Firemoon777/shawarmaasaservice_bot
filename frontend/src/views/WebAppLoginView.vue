<template>
  <div class="text-center">
    {{debug_data}}
<!--    <div class="spinner-border" role="status" v-if="access_granted">-->
<!--      <span class="visually-hidden">Loading...</span>-->
<!--    </div>-->
<!--    <div class="card text-center" v-if="!access_granted">-->
<!--      <img src="/access.png" class="card-img-top" alt="...">-->
<!--      <div class="card-body">-->
<!--        <h5>Для доступа необходимо выполнить вход в приложение.</h5>-->
<!--        Бот получит доступ к вашему нику, имени и фотографии профиля. Это необходимо для идентификации человека, который выполняет заказ. В WebApp версии было также.-->
<!--      </div>-->
<!--    </div>-->
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "WebAppLoginView",
  data() {
    return {
      debug_data: "Загрузка..."
    }
  },
  computed: {
    user_id: function () {
      return  window.Telegram.WebApp.initDataUnsafe.user.id
    },
    first_name: function () {
      return  window.Telegram.WebApp.initDataUnsafe.user.first_name
    },
    last_name: function () {
      return  window.Telegram.WebApp.initDataUnsafe.user.last_name
    },
    photo_url: function () {
      return null
    },
    auth_date: function () {
      return  window.Telegram.WebApp.initDataUnsafe.auth_date
    },
    username: function () {
      return  window.Telegram.WebApp.initDataUnsafe.user.username
    },
    hash: function () {
      return  window.Telegram.WebApp.initDataUnsafe.hash
    },
    access_granted: function () {
      return !!this.hash
    },
    route: function () {
      return this.$route.query.route
    }
  },
  methods: {

  },
  // mounted() {
  //   this.debug_data = window.Telegram.WebApp.initDataUnsafe
  //   // this.debug_data = window.Telegram.WebApp.initData
  //   // console.log(window.Telegram.WebApp)
  // },
  mounted() {
    if(!this.access_granted) return;
    let data = {
      initData: window.Telegram.WebApp.initData,
      user_id: this.user_id,
      hash: this.hash
    }
    let self = this
    axios.post("/login/webapp", data).then(function (response) {
      self.$router.push({
        path: '/'
      })
    }).catch(function (error) {
      self.debug_data = error.response.data
      self.hash = ""
    })
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