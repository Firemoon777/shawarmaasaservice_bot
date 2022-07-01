<template>
    <div class="item-menu is-flex-wrap-wrap is-justify-content-space-between is-justify-content-start">
        <MenuItem v-for="item in this.items" :item="item" v-on:count-changed="agg"/>
    </div>
</template>

<script>
    import axios from 'axios';
    import MenuItem from "../components/MenuItem.vue";
    export default {
        name: "MenuView",
        components: {MenuItem},
        props: ["id"],
        data() {
            return {
                items: [],
                cart: {}
            }
        },
        methods: {
            agg(id, count) {
                console.log("id = " + id + ", count = " + count)
                this.cart[id] = count
                console.log(this.cart)
                window.Telegram.WebApp.show()
            }
        },
        created() {
            axios.get("https://bot.f1remoon.com/api/menu/" + this.id).then((response) => {
                this.items = response.data
                localStorage.items = JSON.stringify(this.items)
            }).catch((error) => {
                console.log(error)
            })
        },
        mounted() {
            let externalScript = document.createElement('script')
            externalScript.setAttribute('src', 'https://telegram.org/js/telegram-web-app.js')
            document.head.appendChild(externalScript)
        },
    }
</script>

<style scoped>
    .item-menu {
        display: flex;
    }
</style>