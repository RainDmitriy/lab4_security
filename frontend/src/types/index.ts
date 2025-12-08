export interface User {
  id: number;
  login: string;
  role: 'user' | 'admin';
  is_author_verified: boolean;
  avatar_url?: string;
}

export interface News {
  id: number;
  title: string;
  content: any; // JSON
  published_at: string;
  author_id: number;
  cover_url?: string
}

export interface Comment {
  id: number;
  text: string;
  published_at: string;
  author_id: number;
  news_id: number;
  author: User;
}