export const colors = {
  textPrimary: "#222222",
  textSecondary: "#666666",
  placeholder: "#999999",
  border: "#CCCCCC",
  error: "#E5484D",
  errorBg: "#FFF1F1",
  success: "#1FA971", // 아이디/이메일 "사용 가능" 등 성공 상태
  buttonDisabled: "#CCCCCC",
  // 프리퀄 코랄 포인트 컬러 (실제 브랜드 hex로 교체 가능)
  coral: "#E5613C",
  coralHover: "#CF5433",
} as const;

export const inputBase: React.CSSProperties = {
  width: "100%",
  height: 44,
  padding: "0 14px",
  fontSize: 14,
  color: colors.textPrimary,
  background: "#FFFFFF",
  border: `1px solid ${colors.border}`,
  borderRadius: 6,
  outline: "none",
  boxSizing: "border-box",
};

export function inputStyle(state: "default" | "error" | "success"): React.CSSProperties {
  if (state === "error") {
    return { ...inputBase, border: `1px solid ${colors.error}` };
  }
  if (state === "success") {
    return { ...inputBase, border: `1px solid ${colors.success}` };
  }
  return inputBase;
}

export const helperTextStyle = (state: "default" | "error" | "success"): React.CSSProperties => ({
  marginTop: 6,
  fontSize: 12,
  lineHeight: 1.4,
  color:
    state === "error" ? colors.error : state === "success" ? colors.success : colors.textSecondary,
});

export const labelStyle: React.CSSProperties = {
  display: "block",
  marginBottom: 6,
  fontSize: 13,
  fontWeight: 500,
  color: colors.textPrimary,
};

export function submitButtonStyle(active: boolean): React.CSSProperties {
  return {
    width: "100%",
    height: 46,
    marginTop: 8,
    fontSize: 15,
    fontWeight: 600,
    color: "#FFFFFF",
    background: active ? colors.coral : colors.buttonDisabled,
    border: "none",
    borderRadius: 6,
    cursor: active ? "pointer" : "not-allowed",
    transition: "background 0.15s ease",
  };
}