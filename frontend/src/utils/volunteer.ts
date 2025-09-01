export interface VolunteerSignupData {
  mobile_money_number: string;
  date_of_birth: string;
  idpassport: string;
  marital_status: string;
  education: string;
  profession: string;
  place_of_work: string;
  reason_to_join: string;
  blood_group: string;
  allergies: string[];
  disabilities: string[];
  languages: string[];
  krcs_trainings: string[];
  additional_skills: string[];
}

export const initialVolunteerForm: VolunteerSignupData = {
  mobile_money_number: "",
  date_of_birth: "",
  idpassport: "",
  marital_status: "",
  education: "",
  profession: "",
  place_of_work: "",
  reason_to_join: "",
  blood_group: "",
  allergies: [],
  disabilities: [],
  languages: [],
  krcs_trainings: [],
  additional_skills: [],
};

export interface SignUp extends VolunteerSignupData {
  firstName: string;
  lastName: string;
  region: string;
  branch: string;
  email: string;
  password: string;
  categoryVolunteer: boolean;
  categoryMember: boolean;
  membershipType: string;
  gender: string;
  phone_number: string;
}

export const initialForm: SignUp = {
  firstName: "",
  lastName: "",
  region: "",
  branch: "",
  email: "",
  password: "",
  categoryVolunteer: false,
  categoryMember: false,
  membershipType: "",
  gender: "",
  phone_number: "",
  ...initialVolunteerForm,
};

export function resetSignUpForm(form: SignUp) {
  form.firstName = "";
  form.lastName = "";
  form.region = "";
  form.branch = "";
  form.email = "";
  form.password = "";
  form.categoryVolunteer = false;
  form.categoryMember = false;
  form.membershipType = "";
  form.gender = "";
  form.phone_number = "";
  form.languages = [];
  form.krcs_trainings = [];
  form.additional_skills = [];
}
