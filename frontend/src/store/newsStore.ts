import { create } from 'zustand';
import type { News } from '../types';
import apiClient from '../api/client';

interface NewsState {
  allNews: News[];
  filteredNews: News[];
  authorsMap: Record<number, string>;
  loading: boolean;
  error: string | null;
  setSearchQuery: (query: string) => void;
  setAuthorFilter: (author: string) => void;
  setDateFrom: (date: string) => void;
  setDateTo: (date: string) => void;
  fetchNews: () => Promise<void>;
  fetchAuthorName: (id: number) => Promise<string>;
}

export const useNewsStore = create<NewsState>((set, get) => ({
  allNews: [],
  filteredNews: [],
  authorsMap: {},
  loading: false,
  error: null,

  setSearchQuery: (query) => {
    const { allNews, authorsMap, authorFilter, dateFrom, dateTo } = get();
    let result = [...allNews];

    if (query) {
      const lowerQuery = query.toLowerCase();
      result = result.filter(n => n.title.toLowerCase().includes(lowerQuery));
    }

    if (authorFilter) {
      const lowerAuthor = authorFilter.toLowerCase();
      result = result.filter(n => {
        const authorName = authorsMap[n.author_id];
        return authorName && authorName.toLowerCase().includes(lowerAuthor);
      });
    }

    if (dateFrom) {
      const from = new Date(dateFrom).getTime();
      result = result.filter(n => new Date(n.published_at).getTime() >= from);
    }
    if (dateTo) {
      const to = new Date(dateTo).getTime();
      result = result.filter(n => new Date(n.published_at).getTime() <= to);
    }

    set({ filteredNews: result });
  },

  setAuthorFilter: (author) => {
    const { allNews, authorsMap, searchQuery, dateFrom, dateTo } = get();
    let result = [...allNews];

    if (searchQuery) {
      const lowerQuery = searchQuery.toLowerCase();
      result = result.filter(n => n.title.toLowerCase().includes(lowerQuery));
    }

    if (author) {
      const lowerAuthor = author.toLowerCase();
      result = result.filter(n => {
        const authorName = authorsMap[n.author_id];
        return authorName && authorName.toLowerCase().includes(lowerAuthor);
      });
    }

    if (dateFrom) {
      const from = new Date(dateFrom).getTime();
      result = result.filter(n => new Date(n.published_at).getTime() >= from);
    }
    if (dateTo) {
      const to = new Date(dateTo).getTime();
      result = result.filter(n => new Date(n.published_at).getTime() <= to);
    }

    set({ filteredNews: result });
  },

  setDateFrom: (date) => {
    const { allNews, authorsMap, searchQuery, authorFilter, dateTo } = get();
    let result = [...allNews];

    if (searchQuery) {
      const lowerQuery = searchQuery.toLowerCase();
      result = result.filter(n => n.title.toLowerCase().includes(lowerQuery));
    }

    if (authorFilter) {
      const lowerAuthor = authorFilter.toLowerCase();
      result = result.filter(n => {
        const authorName = authorsMap[n.author_id];
        return authorName && authorName.toLowerCase().includes(lowerAuthor);
      });
    }

    if (date) {
      const from = new Date(date).getTime();
      result = result.filter(n => new Date(n.published_at).getTime() >= from);
    }
    if (dateTo) {
      const to = new Date(dateTo).getTime();
      result = result.filter(n => new Date(n.published_at).getTime() <= to);
    }

    set({ filteredNews: result });
  },

  setDateTo: (date) => {
    const { allNews, authorsMap, searchQuery, authorFilter, dateFrom } = get();
    let result = [...allNews];

    if (searchQuery) {
      const lowerQuery = searchQuery.toLowerCase();
      result = result.filter(n => n.title.toLowerCase().includes(lowerQuery));
    }

    if (authorFilter) {
      const lowerAuthor = authorFilter.toLowerCase();
      result = result.filter(n => {
        const authorName = authorsMap[n.author_id];
        return authorName && authorName.toLowerCase().includes(lowerAuthor);
      });
    }

    if (dateFrom) {
      const from = new Date(dateFrom).getTime();
      result = result.filter(n => new Date(n.published_at).getTime() >= from);
    }
    if (date) {
      const to = new Date(date).getTime();
      result = result.filter(n => new Date(n.published_at).getTime() <= to);
    }

    set({ filteredNews: result });
  },

  fetchNews: async () => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.get('/news');
      const news = res.data;
      set({ allNews: news, filteredNews: news });
      // Подгружаем имена авторов
      const uniqueAuthorIds = [...new Set(news.map((n: News) => n.author_id))];
      for (const id of uniqueAuthorIds) {
        await get().fetchAuthorName(id);
      }
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Ошибка загрузки новостей' });
    } finally {
      set({ loading: false });
    }
  },

  fetchAuthorName: async (id) => {
    const { authorsMap } = get();
    if (authorsMap[id]) return authorsMap[id];

    try {
      const res = await apiClient.get(`/users/${id}`);
      const login = res.data.login;
      set(state => ({
        authorsMap: { ...state.authorsMap, [id]: login }
      }));
      return login;
    } catch {
      const login = `ID: ${id}`;
      set(state => ({
        authorsMap: { ...state.authorsMap, [id]: login }
      }));
      return login;
    }
  }
}));
