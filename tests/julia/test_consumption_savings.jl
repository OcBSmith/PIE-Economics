using Test
using MacroAIComp

@testset "ConsumptionSavings Tests" begin
    @testset "Equivalence fsolve and optim" begin
        params = default_calibration(ConsumptionSavingParameters)
        W = generate_income_profile("constant", params.T)

        res_fsolve = solve_foc_fsolve(params, W)
        res_optim = solve_direct_optim(params, W)

        @test res_fsolve["C"] ≈ res_optim["C"] atol=1e-3
        @test res_fsolve["B"] ≈ res_optim["B"] atol=1e-3
    end

    @testset "Terminal Condition" begin
        params = default_calibration(ConsumptionSavingParameters)
        for profile in ["constant", "increasing", "retirement"]
            W = generate_income_profile(profile, params.T)
            res_fsolve = solve_foc_fsolve(params, W)
            res_optim = solve_direct_optim(params, W)

            @test abs(res_fsolve["B"][end]) < 1e-5
            @test abs(res_optim["B"][end]) < 1e-5
        end
    end

    @testset "Increasing Income Borrowing" begin
        params = default_calibration(ConsumptionSavingParameters)
        W = generate_income_profile("increasing", params.T)
        res = solve_foc_fsolve(params, W)

        @test any(b -> b < 0.0, res["B"])
        @test res["B"][1] < 0.0

        # slope is negative since beta * (1 + R) < 1
        for t in 1:(params.T - 1)
            @test res["C"][t + 1] < res["C"][t]
        end
    end

    @testset "Retirement Savings Peak" begin
        params = default_calibration(ConsumptionSavingParameters)
        W = generate_income_profile("retirement", params.T)
        res = solve_foc_fsolve(params, W)

        # In Julia (1-indexed), the peak of savings occurs at the end of working life (period 20).
        peak_idx = argmax(res["B"])
        @test peak_idx == 20
        @test all(b -> b > 0.0, res["B"][1:20])

        for t in 20:(params.T - 1)
            @test res["B"][t + 1] < res["B"][t]
        end
    end

    @testset "Discount Factor Sensitivity" begin
        params = ConsumptionSavingParameters(30, 0.99, 0.02, 0.0)
        W = generate_income_profile("constant", params.T)
        res = solve_foc_fsolve(params, W)

        # slope is positive since beta * (1 + R) > 1
        for t in 1:(params.T - 1)
            @test res["C"][t + 1] > res["C"][t]
        end
    end
end
