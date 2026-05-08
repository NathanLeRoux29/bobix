import { describe, it, expect } from "vitest";
import {
  getTimeOfDay,
  getGreetingMessage,
  getRandomTemplateId,
  TEMPLATE_IDS,
} from "../utils/greeting";

describe("getTimeOfDay", () => {
  it("returns matinée for hours 5 to 11", () => {
    expect(getTimeOfDay(5)).toBe("matinée");
    expect(getTimeOfDay(9)).toBe("matinée");
    expect(getTimeOfDay(11)).toBe("matinée");
  });

  it("returns après-midi for hours 12 to 17", () => {
    expect(getTimeOfDay(12)).toBe("après-midi");
    expect(getTimeOfDay(15)).toBe("après-midi");
    expect(getTimeOfDay(17)).toBe("après-midi");
  });

  it("returns soirée for hours 18 to 23 and 0 to 4", () => {
    expect(getTimeOfDay(18)).toBe("soirée");
    expect(getTimeOfDay(23)).toBe("soirée");
    expect(getTimeOfDay(0)).toBe("soirée");
    expect(getTimeOfDay(4)).toBe("soirée");
  });
});

describe("getGreetingMessage", () => {
  it("formats salut template", () => {
    expect(getGreetingMessage("salut", "Marc", 9)).toBe("Salut Marc !");
  });

  it("formats bienvenue template", () => {
    expect(getGreetingMessage("bienvenue", "Marc", 9)).toBe("Bienvenue Marc");
  });

  it("formats pret template", () => {
    expect(getGreetingMessage("pret", "Marc", 9)).toBe(
      "Marc, prêt à travailler ?"
    );
  });

  it("formats hello template with emoji", () => {
    expect(getGreetingMessage("hello", "Marc", 9)).toBe("Hello Marc 👋");
  });

  it("formats bonjour template with matinée", () => {
    expect(getGreetingMessage("bonjour", "Marc", 9)).toBe(
      "Bonjour Marc, bonne matinée"
    );
  });

  it("formats bonjour template with après-midi", () => {
    expect(getGreetingMessage("bonjour", "Marc", 14)).toBe(
      "Bonjour Marc, bonne après-midi"
    );
  });

  it("formats bonjour template with soirée", () => {
    expect(getGreetingMessage("bonjour", "Marc", 20)).toBe(
      "Bonjour Marc, bonne soirée"
    );
  });
});

describe("getRandomTemplateId", () => {
  it("returns a valid template ID", () => {
    const id = getRandomTemplateId();
    expect(TEMPLATE_IDS).toContain(id);
  });

  it("returns different values over multiple calls", () => {
    const results = new Set(Array.from({ length: 50 }, getRandomTemplateId));
    expect(results.size).toBeGreaterThan(1);
  });
});
