export type TimeOfDay = "matinée" | "après-midi" | "soirée";

export type GreetingTemplateId =
  | "salut"
  | "bienvenue"
  | "pret"
  | "hello"
  | "bonjour";

export const TEMPLATE_IDS: GreetingTemplateId[] = [
  "salut",
  "bienvenue",
  "pret",
  "hello",
  "bonjour",
];

export function getTimeOfDay(hour: number): TimeOfDay {
  if (hour >= 5 && hour < 12) return "matinée";
  if (hour >= 12 && hour < 18) return "après-midi";
  return "soirée";
}

export function getGreetingMessage(
  templateId: GreetingTemplateId,
  username: string,
  hour: number
): string {
  const moment = getTimeOfDay(hour);
  const templates: Record<GreetingTemplateId, string> = {
    salut: `Salut ${username} !`,
    bienvenue: `Bienvenue ${username}`,
    pret: `${username}, prêt à travailler ?`,
    hello: `Hello ${username} 👋`,
    bonjour: `Bonjour ${username}, bonne ${moment}`,
  };
  return templates[templateId];
}

export function getRandomTemplateId(): GreetingTemplateId {
  return TEMPLATE_IDS[Math.floor(Math.random() * TEMPLATE_IDS.length)];
}
