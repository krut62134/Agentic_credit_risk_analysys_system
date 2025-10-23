def calculate_debt_to_equity(debt: float, equity: float) -> dict:
    """Calculate debt-to-equity ratio"""
    if equity == 0:
        return {"error": "Equity is zero"}
    
    ratio = debt / equity
    
    # Assess risk level
    if ratio < 0.5:
        risk = "Low"
    elif ratio < 1.0:
        risk = "Moderate"
    elif ratio < 2.0:
        risk = "High"
    else:
        risk = "Very High"
    
    return {
        "debt_to_equity": round(ratio, 2),
        "risk_level": risk
    }


def calculate_debt_to_assets(debt: float, assets: float) -> dict:
    """Calculate debt-to-assets ratio"""
    if assets == 0:
        return {"error": "Assets is zero"}
    
    ratio = debt / assets
    
    if ratio < 0.3:
        risk = "Low"
    elif ratio < 0.5:
        risk = "Moderate"
    else:
        risk = "High"
    
    return {
        "debt_to_assets": round(ratio, 2),
        "risk_level": risk
    }


def calculate_interest_coverage(ebitda: float, interest_expense: float) -> dict:
    """Calculate interest coverage ratio"""
    if interest_expense == 0:
        return {"interest_coverage": "Infinite", "risk_level": "Very Low"}
    
    ratio = ebitda / interest_expense
    
    if ratio > 8:
        risk = "Very Low"
    elif ratio > 4:
        risk = "Low"
    elif ratio > 2.5:
        risk = "Moderate"
    elif ratio > 1.5:
        risk = "High"
    else:
        risk = "Very High"
    
    return {
        "interest_coverage": round(ratio, 2),
        "risk_level": risk
    }


def calculate_current_ratio(current_assets: float, current_liabilities: float) -> dict:
    """Calculate current ratio (liquidity)"""
    if current_liabilities == 0:
        return {"error": "Current liabilities is zero"}
    
    ratio = current_assets / current_liabilities
    
    if ratio > 2.0:
        liquidity = "Strong"
    elif ratio > 1.5:
        liquidity = "Adequate"
    elif ratio > 1.0:
        liquidity = "Marginal"
    else:
        liquidity = "Weak"
    
    return {
        "current_ratio": round(ratio, 2),
        "liquidity_status": liquidity
    }


def assess_credit_rating(debt_to_equity: float, debt_to_assets: float, 
                         interest_coverage: float = None) -> dict:
    """Provide Moody's-style credit rating"""
    
    # Simple rating logic
    if debt_to_equity < 0.3 and debt_to_assets < 0.2:
        if interest_coverage and interest_coverage > 10:
            rating = "Aaa"
        else:
            rating = "Aa"
        risk = "Minimal"
    elif debt_to_equity < 0.5 and debt_to_assets < 0.3:
        rating = "A"
        risk = "Low"
    elif debt_to_equity < 1.0 and debt_to_assets < 0.5:
        rating = "Baa"
        risk = "Moderate"
    elif debt_to_equity < 2.0:
        rating = "Ba"
        risk = "Substantial"
    else:
        rating = "B"
        risk = "High"
    
    return {
        "credit_rating": rating,
        "risk_level": risk,
        "investment_grade": rating in ["Aaa", "Aa", "A", "Baa"]
    }


if __name__ == "__main__":
    # Test the tools
    print("Testing Financial Calculator Tools\n")
    
    # Example: Apple-like numbers
    debt = 100000  # $100B
    equity = 50000  # $50B
    assets = 350000  # $350B
    ebitda = 120000  # $120B
    interest = 3000  # $3B
    
    print("Debt-to-Equity:", calculate_debt_to_equity(debt, equity))
    print("Debt-to-Assets:", calculate_debt_to_assets(debt, assets))
    print("Interest Coverage:", calculate_interest_coverage(ebitda, interest))
    print("Credit Rating:", assess_credit_rating(2.0, 0.29, 40))
