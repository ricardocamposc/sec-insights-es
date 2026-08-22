import { env } from "~/env.mjs";

export const GOOGLE_ANALYTICS_ID = "G-LGHB46ZGWR";
export const INTERCOM_ID = "rx71g1uo";
export const ENABLE_INTERCOM = env.NEXT_PUBLIC_ENABLE_INTERCOM;
// TODO: Populate with your own Sentry DSN:
// https://docs.sentry.io/product/sentry-basics/concepts/dsn-explainer/
export const SENTRY_DSN: string | undefined = undefined;
