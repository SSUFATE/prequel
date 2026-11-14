export type MessageResponse = {
  message: string;
};

export type SignupPayload = {
  login_id: string;
  password: string;
  username: string;
  email: string;
  language: string;
};