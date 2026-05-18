import request from './index'
import type { User } from '../types'

export function login(username: string, password: string) {
  return request.post('/auth/login', { username, password })
}

export function getMe() {
  return request.get<User>('/auth/me')
}
