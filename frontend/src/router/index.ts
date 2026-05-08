import { createRouter, createWebHistory } from "vue-router";
import GreetingView from "../views/GreetingView.vue";
import AppLayout from "../layouts/AppLayout.vue";
import HubView from "../views/HubView.vue";
import NotesView from "../views/NotesView.vue";
import TasksView from "../views/TasksView.vue";
import SettingsView from "../views/SettingsView.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/greeting" },
    { path: "/greeting", component: GreetingView },
    {
      path: "/",
      component: AppLayout,
      children: [
        { path: "hub", component: HubView },
        { path: "notes", component: NotesView },
        { path: "tasks", component: TasksView },
        { path: "settings", component: SettingsView },
      ],
    },
  ],
});
