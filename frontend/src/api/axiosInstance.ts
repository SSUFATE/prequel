import axios from "axios";

console.log("API URL:", process.env.NEXT_PUBLIC_API_URL);

const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

export default axiosInstance;