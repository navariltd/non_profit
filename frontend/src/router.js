import { createRouter, createWebHistory } from "vue-router";
import { usersStore } from "./stores/user";
import { sessionStore } from "./stores/session";
import { useSettings } from "./stores/settings";

let defaultRoute = "/courses";
const routes = [
  {
    path: "/",
    redirect: {
      name: "Courses",
    },
  },
  {
    path: "/user/:username",
    name: "Profile",
    component: () => import("@/pages/Profile.vue"),
    props: true,
    redirect: { name: "ProfileAbout" },
    children: [
      {
        name: "ProfileAbout",
        path: "",
        component: () => import("@/pages/ProfileAbout.vue"),
      },
      {
        name: "ProfileCertificates",
        path: "certificates",
        component: () => import("@/pages/ProfileCertificates.vue"),
      },
      {
        name: "ProfileRoles",
        path: "roles",
        component: () => import("@/pages/ProfileRoles.vue"),
      },
      {
        name: "ProfileEvaluator",
        path: "slots",
        component: () => import("@/pages/ProfileEvaluator.vue"),
      },
      {
        name: "ProfileEvaluationSchedule",
        path: "schedule",
        component: () => import("@/pages/ProfileEvaluationSchedule.vue"),
      },
    ],
  },
  {
    path: "/job-openings",
    name: "Jobs",
    component: () => import("@/pages/Jobs.vue"),
  },
  {
    path: "/job-openings/:job",
    name: "JobDetail",
    component: () => import("@/pages/JobDetail.vue"),
    props: true,
  },
  {
    path: "/job-opening/:jobName/edit",
    name: "JobForm",
    component: () => import("@/pages/JobForm.vue"),
    props: true,
  },
  {
    path: "/persona",
    name: "PersonaForm",
    component: () => import("@/pages/PersonaForm.vue"),
  },
];

let router = createRouter({
  history: createWebHistory("/vmms-portal"),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const { userResource } = usersStore();
  let { isLoggedIn } = sessionStore();
  const { allowGuestAccess } = useSettings();

  try {
    if (isLoggedIn) {
      await userResource.promise;
    }
  } catch (error) {
    isLoggedIn = false;
  }

  if (!isLoggedIn) {
    await allowGuestAccess.promise;
    if (!allowGuestAccess.data) {
      window.location.href = "/login";
      return;
    }
  }
  return next();
});

export default router;
